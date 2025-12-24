"""
ZImage/Lumina2 采样扰动节点

这个节点可以在采样过程中注入噪声扰动，
打破模型的同质化输出，使不同种子能产生更明显的差异。
"""

import torch
import torch.nn.functional as F
import logging


class ZImageTimestepNoise:
    """
    对 timestep/sigma 添加噪声扰动
    这会改变模型对当前去噪步骤的感知，产生不同的输出
    
    支持两种模式：
    - sigma: 适用于传统扩散模型，使用乘性噪声
    - flow: 适用于 Flow Matching 模型（如 ZImage/Lumina2），使用加性噪声
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "sigmas": ("SIGMAS",),
                "mode": (["sigma", "flow"], {
                    "default": "flow",
                    "tooltip": "sigma: 传统扩散模型（乘性噪声）; flow: Flow Matching 模型（加性噪声）"
                }),
                "noise_strength": ("FLOAT", {
                    "default": 0.05, 
                    "min": 0.0, 
                    "max": 2.0, 
                    "step": 0.01,
                    "tooltip": "噪声强度"
                }),
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "tooltip": "噪声种子"
                }),
                "start_percent": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "开始应用噪声的采样进度 (0.0 = 开始)"
                }),
                "end_percent": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "停止应用噪声的采样进度 (1.0 = 结束)"
                }),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"
    CATEGORY = "advanced/model"
    DESCRIPTION = "对 timestep 添加噪声扰动，改变模型对去噪步骤的感知。sigma 模式适用于传统扩散模型，flow 模式适用于 Flow Matching 模型（如 ZImage/Lumina2）。可选遮罩限制影响区域。"

    def patch(self, model, sigmas, mode, noise_strength, seed, start_percent, end_percent, mask=None):
        m = model.clone()
        
        if noise_strength <= 0:
            return (m,)
        
        # 将 sigmas 转换为 list 以便查找
        sigma_list = sigmas.tolist()
        total_steps = len(sigma_list) - 1  # 最后一个是 0
        
        stored_mode = mode
        stored_strength = noise_strength
        stored_seed = seed
        stored_start = start_percent
        stored_end = end_percent
        stored_sigmas = sigma_list
        stored_total_steps = total_steps
        stored_mask = mask
        step_counter = [0]
        
        def unet_wrapper(apply_model_func, args):
            input_x = args["input"]
            timestep = args["timestep"]
            c = args["c"]
            
            step_counter[0] += 1
            current_step = step_counter[0]
            
            # 获取当前 sigma 值
            sigma_val = float(timestep[0]) if timestep.dim() > 0 else float(timestep)
            
            # 在 sigma_list 中查找当前 sigma 的位置来确定进度
            min_diff = float('inf')
            matched_idx = 0
            for i, s in enumerate(stored_sigmas):
                diff = abs(s - sigma_val)
                if diff < min_diff:
                    min_diff = diff
                    matched_idx = i
            
            # 计算进度
            progress = matched_idx / stored_total_steps if stored_total_steps > 0 else 0.0
            progress = max(0.0, min(1.0, progress))
            
            # 检查是否在指定范围内
            in_range = progress >= stored_start and progress <= stored_end
            
            # 准备遮罩（如果有）
            latent_mask = None
            if stored_mask is not None:
                mask_tensor = stored_mask
                if mask_tensor.dim() == 2:
                    mask_tensor = mask_tensor.unsqueeze(0)
                latent_h, latent_w = input_x.shape[2], input_x.shape[3]
                latent_mask = F.interpolate(
                    mask_tensor.unsqueeze(1),
                    size=(latent_h, latent_w),
                    mode='bilinear',
                    align_corners=False
                )
                if latent_mask.shape[0] == 1 and input_x.shape[0] > 1:
                    latent_mask = latent_mask.expand(input_x.shape[0], -1, -1, -1)
                latent_mask = latent_mask.to(device=input_x.device, dtype=input_x.dtype)
            
            # 计算噪声（无论是否在范围内都计算，用于调试显示）
            generator = torch.Generator(device=timestep.device)
            generator.manual_seed(stored_seed + current_step)
            
            t_orig = float(timestep[0]) if timestep.dim() > 0 else float(timestep)
            
            if stored_mode == "sigma":
                noise_factor = 1.0 + (torch.rand(1, generator=generator, device=timestep.device).item() - 0.5) * stored_strength
                noisy_timestep = timestep * noise_factor
            else:  # flow 模式
                # 计算可用空间
                headroom_up = 1.0 - t_orig    # 向上的空间
                headroom_down = t_orig - 0.0  # 向下的空间
                
                # 确定实际可用的噪声范围
                actual_up = min(stored_strength, headroom_up)
                actual_down = min(stored_strength, headroom_down)
                
                # 生成 [0, 1] 随机数，然后映射到 [-actual_down, +actual_up]
                raw = torch.rand(1, generator=generator, device=timestep.device).item()
                total_range = actual_down + actual_up
                
                if total_range > 1e-6:
                    # 映射到可用范围：raw=0 -> -actual_down, raw=1 -> +actual_up
                    actual_delta = raw * total_range - actual_down
                else:
                    actual_delta = 0.0
                
                noisy_timestep = timestep + actual_delta
                # 安全 clamp
                noisy_timestep = torch.clamp(noisy_timestep, 0.0, 1.0)
            
            # 获取数值用于日志
            t_noisy = float(noisy_timestep[0]) if noisy_timestep.dim() > 0 else float(noisy_timestep)
            delta = t_noisy - t_orig
            
            # 调试输出
            if current_step <= 5:
                status = "✓ APPLIED" if in_range else "✗ SKIPPED"
                has_mask = "mask=YES" if latent_mask is not None else "mask=NO"
                if stored_mode == "flow":
                    logging.info(f"[ZImageTimestepNoise] step={current_step}/{stored_total_steps} | progress={progress:.2f} | range=[{stored_start:.2f}, {stored_end:.2f}] | {status}")
                    logging.info(f"[ZImageTimestepNoise]   timestep: {t_orig:.6f} -> {t_noisy:.6f} (delta={delta:+.6f}) | headroom=[↓{headroom_down:.3f}, ↑{headroom_up:.3f}] | {has_mask}")
                else:
                    logging.info(f"[ZImageTimestepNoise] step={current_step}/{stored_total_steps} | progress={progress:.2f} | range=[{stored_start:.2f}, {stored_end:.2f}] | {status}")
                    logging.info(f"[ZImageTimestepNoise]   timestep: {t_orig:.6f} -> {t_noisy:.6f} (delta={delta:+.6f}) | factor={noise_factor:.4f} | {has_mask}")
            
            if not in_range:
                # 不在范围内，使用原始 timestep
                return apply_model_func(input_x, timestep, **c)
            
            # 在范围内，应用噪声
            if latent_mask is not None:
                # 计算两种 timestep 下的结果并混合
                result_original = apply_model_func(input_x, timestep, **c)
                result_noisy = apply_model_func(input_x, noisy_timestep, **c)
                result = result_original * (1 - latent_mask) + result_noisy * latent_mask
                return result
            else:
                # 无遮罩，直接使用扰动后的 timestep
                return apply_model_func(input_x, noisy_timestep, **c)
            
            return apply_model_func(input_x, timestep, **c)
        
        m.set_model_unet_function_wrapper(unet_wrapper)
        
        return (m,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ZImageTimestepNoise": ZImageTimestepNoise,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZImageTimestepNoise": "ZImage Timestep Noise",
}
