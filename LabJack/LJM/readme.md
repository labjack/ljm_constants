# [LabJack LJM Directory](https://labjack.com/support/software/api/ljm/what-ljm-files-are-installed)

This directory contains files for LJM configuration, log output, etc.



## [ljm.log](https://labjack.com/support/software/api/ljm/constants/ljmdebuglogfile)

ljm.log is the default log output file for LJM's logging functionality.



## [ljm_auto_ips.json](https://labjack.com/support/software/api/ljm/function-reference/AutoIPsConfigs)

ljm_auto_ips.json automatically stores LabJack network connection information.



## [ljm_constants.json](https://labjack.com/support/software/api/ljm/constants/ljmconstantsfile)

ljm_constants.json is the default LJM constants file. It contains a JSON description of the LabJack ecosystem. Most importantly, it contains a "registers" array, which describes the registers of LabJack devices, and an "errors" array, which describes LJM and device error codes. There is also an on-line representation of the [device registers](https://labjack.com/support/software/api/modbus/modbus-map).



## [ljm_specific_ips.config](https://labjack.com/support/software/api/ljm/constants/SpecificIPsConfigs)

ljm_specific_ips.config is a configuration file for forcing LJM to manually check specified IP addresses during Open calls or ListAll calls.

ljm_specific_ips.config used to be ljm_special_addresses.config.



## [ljm_startup_configs.json](https://labjack.com/support/software/api/ljm/function-reference/LJMStartupConfigs)

ljm_startup_configs.json is parsed for LJM configurations upon LJM startup.
