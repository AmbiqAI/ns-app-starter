FROM mcr.microsoft.com/devcontainers/base:ubuntu

ARG ACfE=ARMCompiler6.21_standalone_linux-x86_64.tar.gz
ARG FVP=FVP_ARM_Std_Library_11.24_11_Linux64.tgz
ARG ARCH=x86_64

ENV USER=ubuntu

# Update docker image OS
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y upgrade

# Install necessary dependencies
RUN apt-get install -y nano sudo ca-certificates git make cmake lsb-core libx11-dev libxext6 libsm6 libxcursor1 libxft2 libxrandr2 libxt6 libxinerama1 libz-dev lsb xterm telnet dos2unix

# Setup default user
RUN useradd --create-home -s /bin/bash -m $USER && echo "$USER:$USER" | chpasswd && adduser $USER sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/$USER
USER ubuntu

# Install Arm Compiler for Embedded
COPY $ACfE /home/$USER
RUN mkdir /home/$USER/tmp
RUN tar xvfz $ACfE  -C /home/$USER/tmp
RUN /home/$USER/tmp/install_$ARCH.sh --i-agree-to-the-contained-eula --no-interactive -q -f -d /home/$USER/ACfE
RUN rm -rf /home/$USER/tmp
RUN rm $ACfE
ENV PATH "/home/$USER/ACfE/bin:$PATH"

# Install FVP Library
COPY $FVP /home/$USER
RUN mkdir /home/$USER/tmp
RUN tar xvfz $FVP  -C /home/$USER/tmp
RUN /home/$USER/tmp/FVP_ARM_Std_Library.sh --i-agree-to-the-contained-eula --no-interactive -q -f -d /home/$USER/FVP
RUN rm -rf /home/$USER/tmp
RUN rm $FVP
ENV PATH "/home/$USER/FVP/bin:/home/$USER/FVP/FVP_Base:/home/$USER/FVP/FVP_MPS2:/home/$USER/FVP/FVP_VE:/home/$USER/FVP/FVP_BaseR:$PATH"
