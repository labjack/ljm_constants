"""Generate a C header file for the embedded LabJack LJM Modbus Map.
"""
import json
import os
import subprocess

import ljmmm

from labjack import ljm

SRC_FILE = 'LabJack/LJM/ljm_constants.json'
OUTPUT_FILE = 'gen_output/EmbeddedConstants.h'

def init(file, constants_version):
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
    file.write("#define LJM_EC_NumRegs  17\n")
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
    # CRC returned as a string
    return crc

def shorten_reg_name(name):
    bad_chars = '(:)#'
    short_name = ""
    index = ""
    between_bad_chars = False
    for i in name:
        if (i in bad_chars):
            between_bad_chars = True
        if (i.isdigit()):
            # Ignore any digits in (:)
            if (between_bad_chars == False):
                # Pull out entire number from the string
                index += i
        elif (i not in bad_chars):
            if (between_bad_chars == True):
                between_bad_chars = False
            # The shortened name should be any characters not in bad_chars and
            # not any digits
            short_name += i
    return (short_name, index)

def extract_reg_data(reg, reg_dir, conflict_dir):
    short_name, index = shorten_reg_name(reg["name"])
    crc_num = get_crc_val(short_name)
    crc = "{0:#0{1}x}".format(crc_num,10).upper()
    address = reg["address"]
    data_type = get_reg_enum(reg)
    conflict_mode = 0
    #  If there were numbers in the register name
    if (index != ""):
        conflict_mode = 1
        table_name = "LJM_EC_Conflict_" + short_name
        if (table_name in conflict_dir):
            conflict_dir[table_name].append(
                {
                    "index": index,
                    "address": address,
                    "data_type": data_type,
                    "conflict_mode": conflict_mode,
                    "table_name": table_name,
                }
            )
        # We still need to add the register info to the register list and the
        # conflict directory
        else:
            
            reg_dir.append(
                {
                    "crc": crc,
                    "address": len(conflict_dir),
                    "data_type": -999, # TODO: FIGURE THIS OUT
                    "conflict_mode": conflict_mode,
                    "short_name": short_name,
                }
            )
            conflict_dir[table_name] =  []
            conflict_dir[table_name].append(
                {
                    "index": index,
                    "address": address,
                    "data_type": data_type,
                    "conflict_mode": conflict_mode,
                    "table_name": table_name,
                }
            )
    else:
        reg_list_index = len(reg_dir)
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

def print_registers(file, sorted_registers):
    file.write("const LJM_EC_Reg LJM_EC_Regs[] = {\n")
    i = 0
    while i < len(sorted_registers):
        if (i < len(sorted_registers)-1):
            file.write("\t{%s, %d, %d,\t%d},\t\t// %s\n" % (
                sorted_registers[i]["crc"],
                sorted_registers[i]["address"],
                sorted_registers[i]["data_type"],
                sorted_registers[i]["conflict_mode"],
                sorted_registers[i]["short_name"])
            )
        else:
            file.write("\t{%s, %d, %d,\t%d}\t\t// %s\n" % (
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
                file.write("\t{%s, %d, %d, %d},\n" % (
                    conflict_table[i]["index"],
                    conflict_table[i]["address"],
                    conflict_table[i]["data_type"],
                    conflict_table[i]["conflict_mode"])
                )
            else:
                file.write("\t{%s, %d, %d, %d}\n" % (
                    conflict_table[i]["index"],
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
        expand_alt_names=False
    )

    constants_contents = json.loads(ljmmm.read_file(src=SRC_FILE))

    with open(OUTPUT_FILE, 'w') as file:
        init(file, constants_contents["header"]["version"])

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
                # else:
                #     print "Duplicate: %s" % reg["name"]
        # Sort register list by CRC value
        sorted_registers = sorted(reg_dir, key=lambda x: x["crc"])
        print_registers(file, sorted_registers)
        print_conflict_tables(file, conflict_dir)
        print_conflict_directory(file, conflict_dir)
        file.write("\n\n")
        finish(file)


if __name__ == "__main__":
    generate()
