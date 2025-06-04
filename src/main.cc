/**
 * @file main.cc
 * @author Ambiq AITG (support.aitg@ambiq.com)
 * @version 1.0.0
 * @date 2025-04-04
 *
 * @copyright Copyright (c) 2025
 *
 */

// neuralSPOT
#include "ns_ambiqsuite_harness.h"
#include "ns_peripherals_power.h"
// Locals
#include "main.h"

int
main(void)
{

    ns_core_config_t nsCoreCfg = {
        .api = &ns_core_V1_0_0
    };

    NS_TRY(ns_core_init(&nsCoreCfg), "Core Init failed.\b");
    NS_TRY(ns_power_config(&ns_development_default), "Power Init Failed\n");
    ns_itm_printf_enable();
    ns_interrupt_master_enable();

    while (1) {
        ns_printf("Running NS App...\n");
        ns_delay_us(5000000);
    };
}
