# neuralSPOT Application Starter

This repository provides a starter template for building applications with the neuralSPOT SDK. It is designed to be modular—allowing you to add or remove internal neuralSPOT modules as well as a variety of add-on modules.

## Table of Contents

- [neuralSPOT Application Starter](#neuralspot-application-starter)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
  - [Supported Platforms](#supported-platforms)
  - [Repository Structure](#repository-structure)
  - [Available Add-on Modules](#available-add-on-modules)
  - [Adding Add-on Modules](#adding-add-on-modules)
  - [Example: Adding `ns-tileio`](#example-adding-ns-tileio)

---

## Prerequisites

Before you begin, ensure you have the following tools installed:

- **Make**
  Install via your package manager or from [https://www.gnu.org/software/make/](https://www.gnu.org/software/make/)

- **Arm GNU Toolchain**
  Download and install from [https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)

---

## Getting Started

1. **Clone the repository (with submodules)**

   ```bash
   git clone --recurse-submodules https://github.com/AmbiqAI/ns-app-starter.git
   cd ns-app-starter
   ```

2. **Build the application**

   ```bash
   make
   ```

3. **Flash (deploy) the application to your board**

   ```bash
   make deploy
   ```

4. **View application output (SWO output)**

   ```bash
   make view
   ```

---

## Supported Platforms

The neuralSPOT SDK supports multiple Apollo platforms. By default, the target platform is defined in `local_overrides.mk`. To switch platforms, edit the `PLATFORM` variable in that file.

| Platform Identifier             | Description                    |
|---------------------------------|--------------------------------|
| `apollo510_evb`                 | Apollo510 EVB                  |
| `apollo4p_evb`                  | Apollo4 Plus EVB               |
| `apollo4p_blue_kxr_evb`         | Apollo4 Plus Blue KXR EVB      |
| `apollo4p_blue_kbr_evb`         | Apollo4 Plus Blue KBR EVB      |
| `apollo4l_evb`                  | Apollo4 Lite EVB               |
| `apollo4l_blue_evb`             | Apollo4 Lite Blue EVB          |
| `apollo3p_evb`                  | Apollo3 Plus EVB               |

*To change platforms:*

1. Open `local_overrides.mk`.
2. Modify the line:

   ```makefile
   PLATFORM := <desired_platform_identifier>
   ```

---

## Repository Structure

This repository is organized to facilitate modular development. Here’s a high-level overview of its structure:

```bash
ns-app-starter/
├── modules/                 # Add-on modules (git submodules)
├── neuralspot/              # neuralSPOT SDK and its internal modules (git submodule)
├── src/                     # Main application source code
├── local_overrides.mk       # Local overrides (e.g., PLATFORM)
├── Makefile                 # Top-level Makefile
└── README.md                # This document
```

- **modules/**
  Contains any add-on modules you choose to include. Each module is included as a Git submodule (or can be manually copied if you’re not using Git).

- **neuralspot/**
  The neuralSPOT SDK core and its internal modules, tracked as a Git submodule.

- **src/**
  Your application’s source code (C/C++), examples, and any user-specific logic.

- **local_overrides.mk**
  Override variables (such as the target platform).

- **Makefile**
  The main build script. It pulls in settings from `neuralspot/make/*.mk`, compiles code, and provides targets for flashing and viewing output.

## Available Add-on Modules

You can extend your application’s capabilities by including any of the following add-on modules. These are maintained as separate Git repositories and added under the `modules/` directory:

- **[ns-cmsis-nn](https://github.com/AmbiqAI/ns-cmsis-nn)**
  Optimized CMSIS-NN neural network routines for neuralSPOT.

- **[ns-cmsis-dsp](https://github.com/AmbiqAI/ns-cmsis-dsp)**
  Optimized CMSIS-DSP signal-processing routines for neuralSPOT.

- **[ns-features](https://github.com/AmbiqAI/ns-features)**
  Feature extraction helpers optimized for neuralSPOT.

- **[ns-tileio](https://github.com/AmbiqAI/ns-tileio)**
  Tileio BLE/USB support for web applications.

- **[ns-sensors](https://github.com/AmbiqAI/ns-sensors)**
  Collection of sensor drivers (e.g., IMU, microphone) for neuralSPOT.

- **[ns-physiokit](https://github.com/AmbiqAI/ns-physiokit)**
  Physiological data processing (e.g., ECG, PPG) module for neuralSPOT.

- **[ns-tflm](https://github.com/AmbiqAI/ns-tflm)**
  HeliosRT inference engine for TensorFlow Lite Micro (LiteRT) models.

---

## Adding Add-on Modules

To include a new add-on module in your application, follow these steps:

1. **Clone (or add) the module under `modules/`**
   - **If your project is a Git repository** (recommended):

     ```bash
     git submodule add <repository-url> modules/<module-name>
     ```

   - **If you are not using Git**:

     ```bash
     git clone <repository-url> modules/<module-name>
     ```

2. **Include the module in the build**
   Open the top-level `Makefile` and locate the line that defines `modules`. Append your new module path. For example:

   ```makefile
   modules += modules/<module-name>
   ```

3. **Rebuild the application**

   ```bash
   make clean && make
   ```

4. **(Optional) Update your application code**
   If the module provides APIs or headers, update your source files in `src/` to include and use the new functionality.

---

## Example: Adding `ns-tileio`

1. **Add the `ns-tileio` repository**

   ```bash
   git submodule add https://github.com/AmbiqAI/ns-tileio.git modules/ns-tileio
   ```

2. **Edit the Makefile**
   Find the `# neuralSPOT add-on modules` section in the `Makefile`:

   Append:

   ```makefile
   modules += modules/ns-tileio/tio-usb
   modules += modules/ns-tileio/tio-ble
   ```

3. **Rebuild**

   ```bash
   make clean && make
   ```

4. **Use in your code**
   In `src/main.c` (for example):

   ```c
   #include "tio_usb.h"

   tio_usb_context_t g_tio_usb_context = {
        ...
   };

   int main(void)
   {
       NS_TRY(tio_usb_init(&g_tio_usb_context), "Failed to initialize USB Tile I/O");
       // … your application logic …
       return 0;
   }
   ```

---
