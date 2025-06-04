# neuralSPOT Application Starter

This repo serves as a starter template for building applications using the neuralSPOT SDK. This approach allows adding/removing internal NS modules as well as adding a variety of add-on modules.

## Getting Started

1. Clone the repository:

    ```bash
    git clone --recurse-submodules https://github.com/AmbiqAI/ns-app-starter.git
    cd ns-app-starter
    ```

2. Build the application:

    ```bash
    make
    ```

3. Flash the application:

    ```bash
    make deploy
    ```

4. View the application output:

    ```bash
    make view
    ```

## Prerequisites

- [Make](https://www.gnu.org/software/make/)
- [Arm GNU Toolchain](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)

## Supported Platforms

The following platforms are supported by the neuralSPOT SDK:

- **apollo510_evb**: Apollo510 EVB
- **apollo4p_evb**: Apollo4 Plus EVB
- **apollo4p_blue_kxr_evb**: Apollo4 Plus Blue KXR EVB
- **apollo4p_blue_kbr_evb**: Apollo4 Plus Blue KBR EVB
- **apollo4l_evb**: Apollo4 Lite EVB
- **apollo4l_blue_evb**: Apollo4 Lite Blue EVB
- **apollo3p_evb**: Apollo3 Plus EVB

To change the target platform, modify the `PLATFORM` variable in the `make/local_overrides.mk` file.

## Repository Structure

- **make/**: Contains Makefile helpers for building and running the application.
- **modules/**: Contains add-on modules that can be used with the neuralSPOT SDK (git submodules).
- **neuralspot/**: Contains the neuralSPOT SDK and it's internal modules (git submodule).
- **src/**: Contains the main application code.
- **Makefile**: The main Makefile for building the application.

## Available Add-on Modules

The following add-on modules are available for use with the neuralSPOT SDK:

- **[ns-cmsis-nn](https://github.com/AmbiqAI/ns-cmsis-nn)**: Optimized CMSIS-NN module for neuralSPOT
- **[ns-cmsis-dsp](https://github.com/AmbiqAI/ns-cmsis-dsp)**: Optimized CMSIS-DSP module for neuralSPOT
- **[ns-features](https://github.com/AmbiqAI/ns-features)**: Optimized features module for neuralSPOT
- **[ns-tileio](https://github.com/AmbiqAI/ns-tileio)**: Tileio add-on for neuralSPOT
- **[ns-sensors](https://github.com/AmbiqAI/ns-sensors)**: Collection of sensor drivers for neuralSPOT
- **[ns-physiokit](https://github.com/AmbiqAI/ns-physiokit)**: Physiological data processing module for neuralSPOT
- **[ns-tflm](https://github.com/AmbiqAI/ns-tflm)**: HeliosRT inference engine for LiteRT models

## Adding Add-on Modules

To add an add-on module to your application, follow these steps:

1. Clone the add-on module repository into the `modules/` directory.
    ```bash
    git submodule add <repository-url> modules/<module-name>
    ```

    Note: This requires the app to be a git repository. To add modules to a non-git repository, you can manually copy or clone the module into the `modules/` directory.
    ```bash
    git clone <repository-url> modules/<module-name>
    ```

2. Update the `Makefile` to include the new module.
    ```makefile
    modules      += modules/<module-name>
    ```

3. Rebuild the application.
    ```bash
    make clean && make
    ```
