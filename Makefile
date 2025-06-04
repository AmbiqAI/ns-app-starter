include local_overrides.mk
include neuralspot/make/helpers.mk
include neuralspot/make/neuralspot_config.mk
include neuralspot/make/neuralspot_toolchain.mk
include neuralspot/make/jlink.mk

ifeq ($(TOOLCHAIN),arm)
COMPDIR := armclang
else ifeq ($(TOOLCHAIN),arm-none-eabi)
COMPDIR := gcc
endif

libraries    :=
override_libraries :=
lib_prebuilt :=
sources      :=
includes_api :=

local_app_name := main

# neuralSPOT internal modules
modules      := neuralspot/neuralspot/ns-core
modules      += neuralspot/neuralspot/ns-harness
modules      += neuralspot/neuralspot/ns-peripherals
modules      += neuralspot/neuralspot/ns-utils
modules      += neuralspot/neuralspot/ns-uart
modules      += neuralspot/neuralspot/ns-rpc
modules      += neuralspot/neuralspot/ns-ipc

modules      += neuralspot/neuralspot/ns-audio
modules      += neuralspot/neuralspot/ns-features
modules      += neuralspot/neuralspot/ns-i2c
modules      += neuralspot/neuralspot/ns-spi
modules      += neuralspot/neuralspot/ns-usb

# neuralSPOT extern modules
modules      += neuralspot/extern/AmbiqSuite/$(AS_VERSION)
modules      += neuralspot/extern/erpc/R1.9.1
# modules      += neuralspot/extern/CMSIS/CMSIS-DSP-1.16.2
modules      += neuralspot/extern/tensorflow/$(TF_VERSION)

# neuralSPOT add-on modules
modules      += modules/ns-cmsis-nn
modules      += modules/ns-cmsis-dsp

TARGET = $(local_app_name)
sources := $(wildcard src/*.c)
sources += $(wildcard src/*.cc)
sources += $(wildcard src/*.cpp)
sources += $(wildcard src/*.s)

targets  := $(BINDIR)/$(local_app_name).axf
targets  += $(BINDIR)/$(local_app_name).bin

objects      = $(call source-to-object,$(sources))
dependencies = $(subst .o,.d,$(objects))

CFLAGS     += $(addprefix -D,$(DEFINES))
CFLAGS     += $(addprefix -I ,$(includes_api))  # needed for modules


ifeq ($(BOARD),apollo5b)
LINKER_EXT := _sbl
else ifeq ($(BOARD),apollo4p)
LINKER_EXT :=
endif

ifeq ($(TOOLCHAIN),arm)
LINKER_FILE := neuralspot/neuralspot/ns-core/src/$(BOARD)/$(COMPDIR)/linker_script$(LINKER_EXT).sct
else ifeq ($(TOOLCHAIN),arm-none-eabi)
LINKER_FILE := neuralspot/neuralspot/ns-core/src/$(BOARD)/$(COMPDIR)/linker_script$(LINKER_EXT).ld
endif


.PHONY: all
all:

include $(addsuffix /module.mk,$(modules))

all: $(BINDIR) $(libraries) $(override_libraries) $(objects) $(targets)

.PHONY: clean
clean:
ifeq ($(OS),Windows_NT)
	@echo "Windows_NT"
	@echo $(Q) $(RM) -rf $(BINDIR)/*
	$(Q) $(RM) -rf $(BINDIR)/*
else
	$(Q) $(RM) -rf $(BINDIR) $(JLINK_CF)
endif

ifneq "$(MAKECMDGOALS)" "clean"
  include $(dependencies)
endif

$(BINDIR):
	$(Q) $(MKD) -p $@

$(BINDIR)/%.o: %.cc
	@echo " Compiling $(COMPILERNAME) $< to make $@"
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CC) -c $(CFLAGS) $(CCFLAGS) $< -o $@

$(BINDIR)/%.o: %.cpp
	@echo " Compiling $(COMPILERNAME) $< to make $@"
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CC) -c $(CFLAGS) $(CCFLAGS) $< -o $@

$(BINDIR)/%.o: %.c
	@echo " Compiling $(COMPILERNAME) $< to make $@"
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CC) -c $(CFLAGS) $(CONLY_FLAGS) $< -o $@

$(BINDIR)/%.o: %.s
	@echo " Assembling $(COMPILERNAME) $<"
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CC) -c $(ASMFLAGS) $< -o $@


$(BINDIR)/$(local_app_name).axf: $(objects) $(libraries) $(lib_prebuilt) $(override_libraries)
	@echo " Linking $(COMPILERNAME) $@"
	$(Q) $(MKD) -p $(@D)
ifeq ($(TOOLCHAIN),arm)
	$(Q) $(LD) $^ $(LFLAGS) --list=$*.map -o $@
else
	$(Q) $(CC) -Wl,-T,$(LINKER_FILE) -o $@ $^ $(LFLAGS)
endif

ifeq ($(TOOLCHAIN),arm)
$(BINDIR)/$(local_app_name).bin: $(BINDIR)/$(local_app_name).axf
	@echo " Copying $(COMPILERNAME) $@..."
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CP) $(CPFLAGS) $@ $<
	$(Q) $(OD) $(ODFLAGS) $< --output $*.txt
else
$(BINDIR)/$(local_app_name).bin: $(BINDIR)/$(local_app_name).axf
	@echo " Copying $(COMPILERNAME) $@..."
	$(Q) $(MKD) -p $(@D)
	$(Q) $(CP) $(CPFLAGS) $< $@
	$(Q) $(OD) $(ODFLAGS) $< > $(@:.bin=.lst)
endif

$(JLINK_CF):
	@echo " Creating JLink command sequence input file..."
	$(Q) echo "ExitOnError 1" > $@
	$(Q) echo "Reset" >> $@
	$(Q) echo "LoadFile $(BINDIR)/$(TARGET).bin, $(JLINK_PF_ADDR)" >> $@
	$(Q) echo "Exit" >> $@

.PHONY: deploy
deploy: $(JLINK_CF)
	@echo " Deploying $< to device (ensure JLink USB connected and powered on)..."
	$(Q) $(JLINK) $(JLINK_CMD)
	# $(Q) $(RM) $(JLINK_CF)

.PHONY: view
view:
	@echo " Printing SWO output (ensure JLink USB connected and powered on)..."
	$(Q) $(JLINK_SWO) $(JLINK_SWO_CMD)
	# $(Q) $(RM) $(JLINK_CF)

%.d: ;
