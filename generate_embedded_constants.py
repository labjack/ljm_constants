"""Generate a C header file for the embedded LabJack LJM Modbus Map.
"""
import json
import os
import subprocess

import ljmmm

from labjack import ljm

SRC_FILE = 'LabJack/LJM/ljm_constants.json'
OUTPUT_FILE = 'gen_output/EmbeddedConstants.h'

def init(file, constants_version, num_registers):
    file.write("// LabJack Embedded Constants\n")
    file.write("\n")
    file.write("#ifndef LJM_EMBEDDED_CONSTANTS_H\n")
    file.write("#define LJM_EMBEDDED_CONSTANTS_H\n")
    file.write("\n")
    file.write("#define LABJACKM_CONSTANTS_VERSION \"%s\"\n" % (constants_version))
    file.write("\n")
    file.write("#ifdef __cplusplus\n")
    file.write("extern \"C\" {\n")
    file.write("#endif\n")
    file.write("\n")
    file.write("#include \"Defines.h\"\n")
    file.write("\n")
    file.write("#define LJM_EC_version  1\n")
    file.write("#define LJM_EC_NumRegs  %d\n" % num_registers)
    file.write("\n")

def finish(file):
    file.write("#ifdef __cplusplus\n")
    file.write("}\n")
    file.write("#endif\n")
    file.write("\n")
    file.write("#endif // #define LJM_EMBEDDED_CONSTANTS_H\n")

def get_reg_enum(reg):
    return {
        'UINT16': 0,
        'UINT32': 1,
        'INT32': 2,
        'FLOAT32': 3,
        'UINT64':4,
        'BYTE': 99,
        'STRING': 98
    }[reg['type'].upper()]

def make_crc_table(hash_size, table_size, poly, mask):
    table = []
    for i in range(0,table_size):
        r = i << (hash_size - 8)
        last_bit = 1 << (hash_size - 1)
        for j in range(0,8):
            if ((r & last_bit) != 0):
                r = (r << 1) ^ poly
            else:
                r = r << 1
        r = r & mask
        table.append(r)
    return table

def crc32_posix(byte_array, crc_table, mask, init):
    num_bytes = len(byte_array)
    crc32 = init
    for byte in byte_array:
        table_index = ((crc32 >> 24) ^ byte) & 0xFF
        crc32 = (crc32 << 8) ^ crc_table[table_index]

    crc32 = crc32 & mask
    crc32 = crc32 ^ mask
    return crc32

def get_crc_val(reg_name):
    # Below are the parameters for the CRC32/POSIX algorithm
    hash_size = 32
    table_size = 256
    poly = 0x04C11DB7
    mask = 0xFFFFFFFF
    init = 0x00000000
    crc_table = make_crc_table(hash_size, table_size, poly, mask)
    name_bytes = bytearray(reg_name, "ascii")
    crc = crc32_posix(name_bytes, crc_table, mask, init)
    # CRC returned as an integer
    return crc

# Extracts and removes any numbers from the register name
def shorten_reg_name(name):
    bad_chars = '(:)#'
    short_name = ""
    # all_nums holds all parsed out integers
    all_nums = []
    number = ""
    conflict_num = -999
    index_location = -999
    between_bad_chars = False
    same_number = True
    # if (name[0:3] == "I2C"):
    #     name = name[:1] + name[2:]

    for i in name:
        # If we have any of the "bad chars" we will need to use indexing if
        # there are any conflicts
        if (i in bad_chars):
            index_location = len(all_nums)
            between_bad_chars = True
        elif (i.isdigit()):
            # Ignore any digits in (:)
            if (between_bad_chars == False):
                # We cannot figure out the conflict number here if there are
                # multiple numbers in the register, so fix that later if
                # necessary
                number += i
        elif (i not in bad_chars):
            if (number != ""):
                all_nums.append(int(number))
                number = ""
            between_bad_chars = False
            # The shortened name should be any characters not in bad_chars and
            # not any digits
            short_name += i
    if (number != ""):
        all_nums.append(int(number))
    if (len(all_nums) > 0):
        conflict_num = all_nums[0]

    return (short_name, conflict_num, index_location, all_nums)

def extract_reg_data(reg, reg_dir, conflict_dir):
    short_name, conflict_num, index_location, all_nums = shorten_reg_name(reg["name"])
    # CRC as an integer
    crc_num = get_crc_val(short_name)
    # CRC as a hex string
    crc = "{0:#0{1}x}".format(crc_num,10).upper()
    address = reg["address"]
    data_type = get_reg_enum(reg)
    conflict_mode = 0

    #  If there were numbers in the register name
    if (len(all_nums) > 0):
        conflict_mode = 1
        table_name = "LJM_EC_Conflict_" + short_name
        # If we already have a conflict table for this register name
        if (table_name in conflict_dir):
            conflict_dir[table_name].append(
                {
                    "conflict_num": conflict_num,
                    "address": address,
                    "data_type": data_type,
                    "conflict_mode": conflict_mode,
                    "short_name": short_name,
                    "all_nums": all_nums,
                }
            )
        # Else we still need to add the register info to the register list and
        # the conflict directory
        else:
            if (len(all_nums) > 2):
                print("Warning! register %s has more than 2 numbers in it" % reg["name"])
            # We have a conflict so change the data_type to hold number
            # location info
            # If there was a register number in the register name add it as
            # the upper nibble of the data_type entry.
            if (index_location >= 0):
                conflict_dt = "0x" + str(index_location)
            # Otherwise the register does not have an index so the upper nibble
            # should be F
            else:
                conflict_dt = "0xF"
            reg_dir.append(
                {
                    "crc": crc,
                    "address": len(conflict_dir),
                    "data_type": conflict_dt,
                    "conflict_mode": conflict_mode,
                    "short_name": short_name,
                }
            )
            conflict_dir[table_name] =  []
            conflict_dir[table_name].append(
                {
                    "conflict_num": conflict_num,
                    "address": address,
                    "data_type": data_type,
                    "conflict_mode": conflict_mode,
                    "short_name": short_name,
                    "all_nums": all_nums,
                }
            )
    # No numbers in the register name so there are no conflicts, only add the
    # register to the register directory
    else:
        reg_dir.append(
            {
                "crc": crc,
                "address": address,
                "data_type": data_type,
                "conflict_mode": conflict_mode,
                "short_name": short_name,
            }
        )
    return (reg_dir, conflict_dir)

def fix_reg_data_type(reg_dir, short_name, conflict_location):
    # Data type is replaced with two nibbles:
    #   upper nibble holds the location of the register number
    #   lower nibble holds the location of the conflict number
    # The data type already has the upper nibble, add on the lower nibble
    for reg in reg_dir:
        if (reg["short_name"] == short_name):
            # If the location of the conflict number is after the register number in
            # the register name
            if (conflict_location >= int(reg["data_type"],16)):
                conflict_num_index = conflict_location + 1
            else:
                conflict_num_index = conflict_location
            reg["data_type"] += str(conflict_num_index)
            return reg_dir

    # Should not ever get here
    return reg_dir


def check_conflict_tables(conflict_dir, reg_dir):
    # Check the conflict tables for any bad conflict matches
    bad_conflict_name = True
    for table_name in conflict_dir:
        conflict_num = -9999999
        index_number =0
        table = conflict_dir[table_name]
        # Keep searching the numbers pulled from the register name until the
        # proper conflict numbers are found. Conflict numbers will always be at
        # the same index in the list of numbers pulled from the register name
        while (bad_conflict_name == True):
            for i in range(0,len(table)):
                # If the conflict num of two conflict table entries are the
                # same they are not the actual conflict number
                if (table[i]["conflict_num"] == conflict_num):
                    bad_conflict_name = True
                else:
                    conflict_num = table[i]["conflict_num"]
                    bad_conflict_name = False
            if (bad_conflict_name == True):
                index_number += 1
                next_num = table[i]["all_nums"][index_number]
                for i in table:
                    table[i]["conflict_num"] = next_num
        short_name = table[0]["short_name"]
        reg_dir = fix_reg_data_type(reg_dir, short_name, index_number)

    return (conflict_dir, reg_dir)

def print_registers(file, sorted_registers):
    file.write("const LJM_EC_Reg LJM_EC_Regs[] = {\n")
    i = 0
    while i < len(sorted_registers):
        if (i < len(sorted_registers)-1):
            file.write("\t{%s, %d, %s,\t%d},\t\t// %s\n" % (
                sorted_registers[i]["crc"],
                sorted_registers[i]["address"],
                sorted_registers[i]["data_type"],
                sorted_registers[i]["conflict_mode"],
                sorted_registers[i]["short_name"])
            )
        else:
            file.write("\t{%s, %d, %s,\t%d}\t\t// %s\n" % (
                sorted_registers[i]["crc"],
                sorted_registers[i]["address"],
                sorted_registers[i]["data_type"],
                sorted_registers[i]["conflict_mode"],
                sorted_registers[i]["short_name"])
            )
        i += 1
    file.write("};\n\n")

def print_conflict_tables(file, conflict_dir):
    for table_name in conflict_dir:
        conflict_table = conflict_dir[table_name]
        file.write("const LJM_EC_Reg %s[] = {\n" % table_name)
        i = 0
        while i < len(conflict_table):
            if (i < len(conflict_table)-1):
                file.write("\t{%d, %d, %d, %d},\n" % (
                    conflict_table[i]["conflict_num"],
                    conflict_table[i]["address"],
                    conflict_table[i]["data_type"],
                    conflict_table[i]["conflict_mode"])
                )
            else:
                file.write("\t{%d, %d, %d, %d}\n" % (
                    conflict_table[i]["conflict_num"],
                    conflict_table[i]["address"],
                    conflict_table[i]["data_type"],
                    conflict_table[i]["conflict_mode"])
                )
            i += 1
        file.write("};\n")

def print_conflict_directory(file, conflict_dir):
    file.write("const LJM_EC_Conflict_Directory LJM_EC_ConflictDirectory[] = {\n")
    i = 0
    for table_name in conflict_dir:
        if (i < len(conflict_dir)-1):
            file.write("\t{%s, %d},\n" % (
                table_name,
                len(conflict_dir[table_name]))
            )
        else:
            file.write("\t{%s, %d}\n" % (
                table_name,
                len(conflict_dir[table_name]))
            )
        i +=1
    file.write("};\n")

def generate():
    modbus_maps = ljmmm.get_device_modbus_maps(
        src=SRC_FILE,
        expand_names=False,
        expand_alt_names=True
    )

    constants_contents = json.loads(ljmmm.read_file(src=SRC_FILE))
    reg_names = []
    reg_dir = []
    conflict_dir = {}
    for device in modbus_maps:
        for reg in modbus_maps[device]:
            # Remove duplication by name. By address would omit altnames
            name = reg["name"]
            if (not name in reg_names):
                reg_names.append(name)
                reg_dir, conflict_dir = extract_reg_data(reg, reg_dir, conflict_dir)

    num_registers = len(reg_dir)
    with open(OUTPUT_FILE, 'w') as file:
        init(file, constants_contents["header"]["version"], num_registers)
        conflict_dir, reg_dir = check_conflict_tables(conflict_dir, reg_dir)
        # Sort register list by CRC value
        sorted_registers = sorted(reg_dir, key=lambda register: register["crc"])
        print_registers(file, sorted_registers)
        print_conflict_tables(file, conflict_dir)
        print_conflict_directory(file, conflict_dir)
        file.write("\n\n")
        finish(file)


if __name__ == "__main__":
    generate()
