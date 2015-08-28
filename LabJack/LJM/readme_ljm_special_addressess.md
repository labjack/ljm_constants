# LJM Special Addresses (`LJM_SPECIAL_ADDRESSES_FILE`)

LJM Special Addresses are IP addresses that LJM will check whenever a ListAll or Open function is called with a network (TCP-based / UDP) `ConnectionType` parameter. During such `ListAll` and `Open` calls, LJM always broadcasts via UDP to `INADDR_BROADCAST` (255.255.255.255) to find LabJack device connections as well as attempting to connect to each of the LJM Special Addresses. This allows for TCP LabJack devices to be found on a subnets that do not permit UDP broadcasts.

By default, LJM parses `ljm_special_addresses.config` on startup and adds all IP addresses contained within with as LJM Scan Addresses. `ljm_special_addresses.config` is located in the same directory as this file. If it does not exist, you may create it.

Contact your network administrator to ensure that the LJM Special Addresses will be reachable via TCP. You can also ping those addresses to ensure that they are reachable. See the `LJM_SPECIAL_ADDRESSES_STATUS` section below for error information.



## Syntax of `ljm_special_addresses.config`

 - Whitespace is ignored.
 - Empty lines and lines starting with // are ignored.
 - All other lines are expected to contain one IP address.



## Relevant LJM Configurations

To read or write LJM configurations, use the following functions:

 - `LJM_ReadLibraryConfigStringS`
 - `LJM_ReadLibraryConfigS`
 - `LJM_WriteLibraryConfigStringS`
 - `LJM_WriteLibraryConfigS`

For more information on LJM configurations, see:
http://labjack.com/support/ljm/users-guide/function-reference/library-configuration-functions


### Configuration Parameter: `LJM_SPECIAL_ADDRESSES_FILE`
type: string

`LJM_SPECIAL_ADDRESSES_FILE` determines which file is used by LJM for the Special Addresses. Upon writing, the specified file is parsed and the contents are added as LJM Special Addresses. By default, the file path specified by `LJM_SPECIAL_ADDRESSES_FILE` is only parsed on LJM startup, so changes made to the file will not affect running LJM processes unless `LJM_WriteLibraryConfigStringS(LJM_SPECIAL_ADDRESSES_FILE, ...)` is called.

Using "default" or an empty string as the value will set `LJM_SPECIAL_ADDRESSES_FILE` to the default location. For example:

    error = LJM_WriteLibraryConfigStringS(LJM_SPECIAL_ADDRESSES_FILE, "default");


### Configuration Parameter: `LJM_SPECIAL_ADDRESSES_STATUS`
type: string

Shows what the status of LJM Special Addresses is. Read `LJM_SPECIAL_ADDRESSES_STATUS` to confirm that LJM loaded the startup `LJM_SPECIAL_ADDRESSES_FILE` without error. Possible values:

 - "Success. File: file_path, IPs: [comma-separated_list_of_IP_addresses]"
 - "File load failure: file_path"
 - "Permission denied: IP_address"

A "permission denied" error probably indicates that the specified IP address was a broadcast address.



## Setting `LJM_SPECIAL_ADDRESSES_FILE` in `ljm_startup_configs.json`

LJM will load `ljm_startup_configs.json` before it parses the file specified by `LJM_SPECIAL_ADDRESSES_FILE`, so `LJM_SPECIAL_ADDRESSES_FILE` can be set in `ljm_startup_configs.json`. See `ljm_startup_configs.json` for more information.

