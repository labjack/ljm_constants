# LJM Scan Addresses (`LJM_SCAN_ADDRESSES_FILE`)

LJM Scan Addresses are IP addresses that LJM will check whenever a ListAll or Open function is called with a TCP-like `ConnectionType` parameter. During relevant `ListAll` and `Open` functions, LJM broadcasts on `INADDR_BROADCAST` (255.255.255.255) to find LabJack device connections, so LJM Scan Addresses allow for a TCP LabJack device to be placed on different subnet that will not be reachable by a `INADDR_BROADCAST` broadcast.

By default, LJM parses `ljm_scan_addresses.config` on startup and adds all IP addresses contained within with as LJM Scan Addresses. `ljm_scan_addresses.config` is located in the same directory as this file. If it does not exist, you may create it.

To broadcast to a subnet, add that subnet's broadcast address. For example, the broadcast address for subnet 192.168.1.0 with subnet mask 255.255.255.0 is 192.168.1.255.

Contact your network administrator to ensure that the intended LJM Scan Addresses will be reachable. For example, subnets may not permit broadcasts and firewalls may not permit traffic. Note that the LJM Scan Addresses are scanned via UDP.


## Syntax of `ljm_scan_addresses.config`

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

### Configuration Parameter: `LJM_SCAN_ADDRESSES_FILE`
type: string

`LJM_SCAN_ADDRESSES_FILE` determines which file is used by LJM for the scan addresses. Upon writing, the specified file is parsed and the contents are added as LJM Scan Addresses. By default, the file path specified by `LJM_SCAN_ADDRESSES_FILE` is only parsed on LJM startup, so changes made to the file will not affect running LJM processes unless `LJM_WriteLibraryConfigStringS(LJM_SCAN_ADDRESSES_FILE, ...)` is called.

Using "default" as the value will set `LJM_SCAN_ADDRESSES_FILE` to the default location. For example:

    error = LJM_WriteLibraryConfigStringS(LJM_SCAN_ADDRESSES_FILE, "default");


### Configuration Parameter: `LJM_SCAN_ADDRESSES_STATUS`
type: To be decided when Rory figures out if there's reasons to use string vs bool

When `LJM_SCAN_ADDRESSES_FILE` is not set manually using `LJM_WriteLibraryConfigStringS`, read `LJM_SCAN_ADDRESSES_STATUS` to confirm that LJM loaded the startup `LJM_SCAN_ADDRESSES_FILE` without error. Possible values:

 - Something TBD indicating success
 - Other TBD thing indicating failure
 - Possibly that's all


## Setting `LJM_SCAN_ADDRESSES_FILE` in `ljm_startup_configs.json`

LJM will load `ljm_startup_configs.json` before it parses the file specified by `LJM_SCAN_ADDRESSES_FILE`, so `LJM_SCAN_ADDRESSES_FILE` can be set in `ljm_startup_configs.json`. See `ljm_startup_configs.json` for more information.

