"""Logic for loading LabJack Modbus Map Markup notation modbus maps.

@author Sam Pottinger
@license GNU GPL v3
"""


import copy
import json
import re
from sets import Set

DEFAULT_FILE_NAME = "ljm_constants/LabJack/LJM/ljm_constants.json"
ACCESS_RESTRICTIONS_STRS = {
    "R": {"read": True, "write": False},
    "RW": {"read": True, "write": True},
    "W": {"read": False, "write": True}
}
DATATYPE_SIZES_IN_REGISTERS = {
    "BYTE": 1,
    "FLOAT32": 2,
    "FLOAT": 2,
    "UINT16": 1,
    "UINT32": 2,
    "UINT64": 4,
    "INT16": 1,
    "INT32": 2,
    "INT64": 4,
    "STRING": None
}


def read_file(src):
    """Read a file and return the contents."""
    with open(src) as f:
        contents = f.read().decode("utf-8","ignore")
    return contents


def get_raw_registers_data(src=DEFAULT_FILE_NAME):
    """Load information about registers from constants JSON file.

    @keyword src: The name of the file to open. Defaults to DEFAULT_FILE_NAME.
    @type src: str
    @return: Raw JSON data dictionary loaded from source file.
    @rtype: dict
    """
    json_contents = json.loads(read_file(src))
    regular_registers = json_contents["registers"]
    if "registers_beta" in json_contents:
        regular_registers.extend(json_contents["registers_beta"])
    return regular_registers


def generate_int_enumeration(src):
    """Generate versions of a string with an enumerated sequence added in.

    Generate variations of a string as a list with an enumerated sequence of
    integers added in. For example (test#, 1, 3) would yield [test1, test2,
    test3] and (test#, 0, 4, 2) would yield [test0, test2, test4]

    @param src: The tuple to generate the enumeration from. First element should
                be the string, the second element the starting integer, and the
                third the ending integer (inclusive). Third optional value
                provides interval between numbers in the enumeration
    @type src: tuple
    @return: Resulting string
    @rtype: iterable of str
    """
    template_str = src[0]
    start_num = int(src[1])
    end_num = int(src[2])
    if src[3] != "" and src[3] != None:
        interval = int(src[3])
    else:
        interval = 1
    afterwards = src[4]

    numbers = range(start_num, end_num+1, interval)
    return map(lambda x: "%s%d%s" % (template_str, x, afterwards), numbers)


def interpret_ljmmm_field(src):
    """Interpret a small string of LabJack Modbus Map Markup field notation.

    Supported notation features:
        "%s\#%s": Ignored
        "%s#(%d:%d): Generate strings with values from first to second number in
                     parentheses. See generate_int_enumeration for more info.
        "%s#(%d:%d:%d): Generate strings with values from first to second
                        number in parentheses with an interval of third number
                        between them. See generate_int_enumeration for more
                        info.

    @param src: The code to execute.
    @type src: str
    @return: Result of running the snippet.
    """
    # Interpret string enumeration (of form "%s#(%d:%d)")
    enumeration_results = re.findall(
        "(.*)\#\((\d+)\:(\d+)\:?(\d+)?\)(.*)",
        src
    )
    if enumeration_results:
        enumeration_tuple = enumeration_results[0]
        result = generate_int_enumeration(enumeration_tuple)
        return map(lambda x: interpret_ljmmm_field(x), result)

    src = src.replace("#pound", "#")
    return src


def enumerate_addresses(start_address, num_addresses, reg_per_address):
    """Generate addresses through enumerating a sequence of numbers.

    @param start_address: The address to start the sequence on.
    @type start_address: int
    @param num_addresses: The number of addresses to generate in the sequence.
    @type num_addresses: int
    @param reg_per_address: The number of registers between each address in
                            this sequence
    @return: Generated address numbers.
    @rtype: list of int
    """
    end_address = start_address + num_addresses * reg_per_address
    return range(start_address, end_address+1, reg_per_address)


def get_datatype_size(datatype_name):
    """Get the number of registers a datatype requires.

    @param datatype_name: The name of the datatype to get the size for.
    @type datatype_name: str
    @return: Number of registers the given datatype takes up or None if the
             given datatype is valid but does not have a fixed size.
    @rtype: int
    @raise ValueError: Raised if datatype_name is not recognized.
    """
    if not datatype_name in DATATYPE_SIZES_IN_REGISTERS:
        raise ValueError(
            "%s is not a known data type." % datatype_name
        )

    return DATATYPE_SIZES_IN_REGISTERS[datatype_name]


def interpret_firmware(firmware):
    """Turn a non-explicit firmware descriptor to an explicit descriptor.

    Interpret a device firmware descriptor, making a non-explicit one into an
    explicit one. So "U3" would return {"device": "U3", "fwmin": 0}. It
    assumes all dictionaries are already explicit descriptors and does not touch
    them. It also assumes all strings are device names.

    @param firmware: The firmware descriptor to interpret.
    @type firmware: dict or str
    @return: Explicit firmware descriptor.
    @rtype: dict
    @raise TypeError: Thrown if firmware is not a dict or a str.
    """
    if isinstance(firmware, basestring):
        return {"device": firmware, "fwmin": 0}
    elif isinstance(firmware, dict):
        return firmware
    else:
        raise TypeError(
            "Provided firmware descriptor invalid: %s" % str(firmware)
        )


def interpret_access_descriptor(descriptor):
    """Interpret a string with info about the access restrictions to a register.

    Interpret a string with access restriction information for a register. For
    example R becomes {"read": True, "write": False}. Assumes all dictionaries
    are already valid dictionaries with access restriction information.

    @param descriptor: The descriptor to interpret.
    @type descriptor: str or dict
    @return: Dictionary with explicit read / write restrictions or the
             dictionary passed in if descriptor was of type dict.
    @rtype: dict
    @raise ValueError: Thrown if descriptor was not recognized.
    """
    if isinstance(descriptor, dict):
        return descriptor

    if not descriptor in ACCESS_RESTRICTIONS_STRS:
        raise ValueError(
            "%s not a valid access restrictions descriptor" % descriptor
        )

    return ACCESS_RESTRICTIONS_STRS[descriptor]


def parse_register_data(raw_register_dict, expand_names=False):
    """Parse information about a single register.

    Loads and interprets register information from the given dictionary
    which can contain LabJack Modbus Map Markup strings, device firmware
    descriptor shorthands, string access restriction descriptors, and other
    raw data. For more information see LabJack Constants Markup notation
    documentation.

    The dictionaries in the resulting list will be in the form of:
    {
        "address": int,
        "name": str,
        "type": str,
        "devices": [
            {
                "device": str,
                "fwmin": float / int,
                "description": str
            }
        ],
        "readwrite": {"read": bool, "write": bool},
        "tags": list of str,
        "default": float / int / None,
        "isBuffer": bool,
        "streamable": bool,
        "constants": [
            {"name": str, "value": float / int}
        ]
    }

    If expand_names == True, all names will be enumerated such that
    DAC#(0:1) will result in two dictionaries, one with
    ret_dict["name"] == "DAC#0" and another with ret_dict["name"] == "DAC#1".
    Otherwise, DAC#(0:1) will result in one dictionary with an unmodified name.

    @param raw_register_dict: Raw dictionary of register information.
    @type raw_register_dict: dict.
    @param expand_names: Choose whether or not to expand the register names
    @type expand_names: bool
    @return: List of interpreted dictionaries.
    @rtype: list of dict
    """
    if expand_names:
        names = interpret_ljmmm_field(raw_register_dict["name"])
    else:
        names = raw_register_dict["name"]
    if isinstance(names, basestring):
        names = [names]

    datatype_str = raw_register_dict["type"]
    datatype_size = get_datatype_size(datatype_str)
    devices = map(lambda x: interpret_firmware(x), raw_register_dict["devices"])
    access_restrictions = interpret_access_descriptor(
        raw_register_dict["readwrite"]
    )

    tags = raw_register_dict.get("tags", [])

    # Interpret addresses
    start_address = raw_register_dict["address"]
    num_addresses = len(names)
    if datatype_size == None:
        addresses = [start_address]
    else:
        addresses = enumerate_addresses(
            start_address,
            num_addresses,
            datatype_size
        )
    name_address_pairs = zip(names, addresses)

    description = raw_register_dict.get("description", "")
    default = raw_register_dict.get("default", None)
    streamable = raw_register_dict.get("streamable", False)
    isBuffer = raw_register_dict.get("isBuffer", False)
    constants = raw_register_dict.get("constants", [])

    # Generate resulting dicts
    ret_list = []
    for (name, address) in name_address_pairs:
        ret_list.append(
            {
                "address": address,
                "name": name,
                "type": datatype_str,
                #"numregs": datatype_size,
                "devices": devices,
                "readwrite": access_restrictions,
                "tags": tags,
                "description": description,
                "default": default,
                "streamable": streamable,
                "isBuffer": isBuffer,
                "constants": constants
            }
        )

    # Handle alternative names
    alt_names = raw_register_dict.get("altnames", [])
    if len(alt_names) > 0:
        alt_names_dict = copy.deepcopy(raw_register_dict)
        del alt_names_dict["altnames"]
        for name in filter(lambda x: x != "", alt_names):
            alt_names_dict["name"] = name
            ret_list.extend(parse_register_data(alt_names_dict, expand_names))

    return ret_list


def interpret_tags(tags, tags_base_url='http://labjack.com/support/modbus/tags'):
    """Converts a list of valid tag names into a list of html links.

    Converts a list of valid tag names into a list of html links. For
    example, interpret_tags(["AIN", "CONFIG"], 'labjack.com/path/to/tags/')
    could become something like:
    [
        "<a class='tag-link' href='labjack.com/path/to/tags/AIN>AIN</a>",
        "<a class='tag-link' href='labjack.com/path/to/tags/CONFIG>CONFIG</a>"
    ]

    @keyword tags: The list of tags to convert into links
    @type tags: list of str
    @keyword tags_base_url: The base url used to create the links
    @type tags_base_url: str
    @return: list of str html links
    """
    return map(lambda x: "<a class=\'tag-link\' href=" + tags_base_url +
                "/" + x + ">" + x + "</a>", tags)


def get_registers_data(src=DEFAULT_FILE_NAME, expand_names=False,
    inc_orig=False):
    """Load and parse information about registers from JSON constants file.

    Loads and interprets registers information from the given JSON constants
    file, in the form output by parse_register_data.

    If expand_names, names will be enumerated such that DAC#(0:1) will result in
    two dictionaries, one with ret_dict["name"] == "DAC#0" and another with
    ret_dict["name"] == "DAC#1"

    For more information see LabJack Modbus Map Markup notation
    documentation.

    @keyword src: The name of the file to open. Defaults to DEFAULT_FILE_NAME.
    @type src: str
    @keyword expand_names: Flag to indicate if LJMMM fields should be
        interpreted, expanding register entries from AIN#(0:2) to AIN#0, AIN#1,
        and AIN#2. Defaults to False.
    @type expand_names: bool
    @keyword inc_orig: Flag to indicate if the results should be zipped in with
        the original register values. Defaults to False.
    @type inc_orig: bool
    @return: dict
    """
    raw_data = get_raw_registers_data(src=src)
    ret_list = []
    for entry in raw_data:
        if inc_orig:
            ret_list.append(parse_register_data(entry, expand_names))
        else:
            ret_list.extend(parse_register_data(entry, expand_names))

    if inc_orig:
        return zip(raw_data, ret_list)
    else:
        return ret_list


def get_device_modbus_maps(src=DEFAULT_FILE_NAME, expand_names=False,
    inc_orig=False):
    """Load register info from JSON constants file and structure by device.

    Loads and interprets registers information from the given JSON constants
    file and structures it by device in the form of:
    {
        "U3":
        [
            {
                "name": str,
                "address": int,
                "type": str,
                "fwmin": float / int,
                "read": bool,
                "write": bool,
                "tags": list of str,
                ...
            }
        ]
    }
    The list of dictionaries for each device type will be sorted by address.

    TODO: Add param to specify this (currenly doesn't expand the register
    names in this way):
    All names will be enumerated such that DAC#(0:1) will result in two
    dictionaries, one with ret_dict["name"] == "DAC#0" and another with
    ret_dict["name"] == "DAC#1".

    All alternative names will be given their own individual entry so
    an address with two alternative names will correspond to three elements
    in the returned lists.

    @keyword src: The name of the file to open. Defaults to DEFAULT_FILE_NAME.
    @type src: str
    @keyword expand_names: Flag to indicate if LJMMM fields should be
        interpreted, expanding register entries from AIN#(0:2) to AIN#0, AIN#1,
        and AIN#2. Defaults to False.
    @type expand_names: bool
    @keyword inc_orig: Flag to indicate if the results should be zipped in with
        the original register values. Defaults to False.
    @type inc_orig: bool
    @return: dict
    """
    registers_data = get_registers_data(src=src, expand_names=expand_names,
        inc_orig=inc_orig)
    device_maps = {}

    if inc_orig:
        preped_registers_data = []
        for (orig, new_collection) in registers_data:
            for new in new_collection:
                preped_registers_data.append((orig, new))
    else:
        preped_registers_data = registers_data

    for register in preped_registers_data:
        if inc_orig: reg_devices = register[1]["devices"]
        else: reg_devices = register["devices"]

        for device in reg_devices:

            device_name = device["device"]
            if not device_name in device_maps:
                device_maps[device_name] = []
            device_reg_list = device_maps[device_name]

            if inc_orig: new_entry = copy.deepcopy(register[1])
            else: new_entry = copy.deepcopy(register)

            min_firmware = device.get("fwmin", 0)
            new_entry["fwmin"] = min_firmware
            new_entry["deviceDescription"] = device.get("description", "")
            del new_entry["devices"]

            access_permissions = new_entry["readwrite"]
            read_val = access_permissions["read"]
            write_val = access_permissions["write"]
            new_entry["read"] = read_val
            new_entry["write"] = write_val
            del new_entry["readwrite"]

            if inc_orig:
                new_entry["description"] = register[1].get("description", "")
                new_entry["constants"] = register[0].get("constants", [])
            else:
                new_entry["description"] = register.get("description", "")
                new_entry["constants"] = register.get("constants", [])

            # TODO: Something better
            new_entry.pop("numregs", None)

            if inc_orig:
                device_reg_list.append((register[0], new_entry))
            else:
                device_reg_list.append(new_entry)

    return device_maps

def get_errors(src=DEFAULT_FILE_NAME):
    """Load LJM and LJM-supported-device errors."""
    contents = read_file(src)
    return json.loads(contents)["errors"]
