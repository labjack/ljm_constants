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

def output_reg(file, reg):
    name = reg['name']
    file.write("static const char * const LJM_%s = \"%s\";\n" % (name, name))
    file.write("enum { LJM_%s_ADDRESS = %d };\n" % (name, reg['address']))
    file.write("enum { LJM_%s_TYPE = %d };\n" % (name, get_reg_enum(reg)))
    file.write("\n")

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
    # below are the parameters for the CRC32/POSIX algorithm
    hash_size = 32
    table_size = 256
    poly = 0x04C11DB7
    mask = 0xFFFFFFFF
    init = 0x00000000
    crc_table = make_crc_table(hash_size, table_size, poly, mask)
    name_bytes = bytearray(reg_name, 'ascii')
    crc = crc32_posix(name_bytes, crc_table, mask, init)
    return hex(crc)



def extract_reg_data(reg):
    bad_chars = '(:)#'
    # remove any numbers and 'bad chars' from the register name
    # still remove number from I2C registers?
    short_name = str.join([i for i in reg['name'] if not (i.is(digit) or i in bad_chars)])
    if (len(short_name) != len(reg['name'])):
        conflict_mode = 1
        # if there was more than one number in the string then 
        # we need to set the conflict mode
        if (len(short_name) < len(reg['name'])-1):
        else:
            # how to differentiate I2C register or DAC1_FREQUENCY_OUT_ENABLE
            # from something like DIO_EF_CLOCK1?
            data_type = 0xF0
    else:
        crc_val = get_crc_val(reg['name'])
        address = reg['address']

        conflict_mode = 0


def generate():
    modbus_maps_expanded = ljmmm.get_device_modbus_maps(
        src=SRC_FILE,
        expand_names=True,
        expand_alt_names=True
    )

    constants_contents = json.loads(ljmmm.read_file(src=SRC_FILE))

    with open(OUTPUT_FILE, 'w') as file:
        init(file, constants_contents['header']['version'])

        reg_names = []
        for device in modbus_maps_expanded:
            for reg in modbus_maps_expanded[device]:

                # Remove duplication by name. By address would omit altnames
                name = reg['name']
                if (not name in printed):
                    reg_names.append(name)
                    output_reg(file, reg)
                # else:
                #     print "Duplicate: %s" % reg["name"]

        finish(file)


if __name__ == "__main__":
    generate()
