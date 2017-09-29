"""Generate a C header file for the LabJack LJM Modbus Map.
"""
import json
import os
import subprocess

import ljmmm

SRC_FILE = 'LabJack/LJM/ljm_constants.json'
OUTPUT_FILE = 'gen_output/LabJackMModbusMap.h'
SANITY_TEST_FILE = 'gen_test/test_c_header.c'

def init(file, constants_version):
    file.write("// LabJack LJM Modbus Map constants\n")
    file.write("#ifndef LABJACKM_MODBUS_MAP_HEADER\n")
    file.write("#define LABJACKM_MODBUS_MAP_HEADER\n")
    file.write("\n")
    file.write("#define LABJACKM_CONSTANTS_VERSION \"%s\"\n" % (constants_version))
    file.write("\n")
    file.write("#ifdef __cplusplus\n")
    file.write("extern \"C\" {\n")
    file.write("#endif\n")
    file.write("\n")

def finish(file):
    file.write("#ifdef __cplusplus\n")
    file.write("}\n")
    file.write("#endif\n")
    file.write("\n")
    file.write("#endif // #define LABJACKM_MODBUS_MAP_HEADER\n")

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

def sanity_test():
    include_dir = os.path.split(OUTPUT_FILE)[0]
    subprocess.check_call([
        'gcc',
        '-o', 'gen_test/test_c_header',
        SANITY_TEST_FILE,
        '-I%s' % include_dir
    ])

    ret = subprocess.call(['gen_test/test_c_header'])
    if ret != 0:
        raise Exception("Expected output to be 0, but was: %d" % ret)

def generate():
    modbus_maps_expanded = ljmmm.get_device_modbus_maps(
        src=SRC_FILE,
        expand_names=True,
        expand_alt_names=True
    )

    constants_contents = json.loads(ljmmm.read_file(src=SRC_FILE))

    with open(OUTPUT_FILE, 'w') as file:
        init(file, constants_contents['header']['version'])

        printed = []
        for device in modbus_maps_expanded:
            for reg in modbus_maps_expanded[device]:

                # Remove duplication by name. By address would omit altnames
                name = reg['name']
                if (not name in printed):
                    printed.append(name)
                    output_reg(file, reg)
                # else:
                #     print "Duplicate: %s" % reg["name"]

        finish(file)

    sanity_test()

if __name__ == "__main__":
    generate()
