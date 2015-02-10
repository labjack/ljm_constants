"""validate.py

Verifies that ljm_constants.json is not obviously invalid.
"""
import sys
import ljmmm

def validate(json_file_path):
    """Validates json_file_path as ljm constants JSON. Exits with non-zero on error."""
    print 'Checking JSON file...'
    try:
        json_map = ljmmm.get_device_modbus_maps(
            json_file_path,
            expand_names=True,
            inc_orig=True
        )
    except Exception as e:
        print '[ERROR] JSON file could not be parsed. Please check. (' + str(e) + ')'
        exit(1)

    print 'Checking register map duplicates...'
    for device in json_map:
        previous_names = []
        previous_addresses = {}
        device_registers = json_map[device]

        for register in device_registers:
            reg_name = register[1]['name']

            if reg_name in previous_names:
                print 'Duplicate entries for %s found.' % reg_name
                exit(1)
            previous_names.append(reg_name)

            reg_addr = register[1]['address']
            if previous_addresses.has_key(reg_addr) and previous_addresses[reg_addr]['name'] != register[0]['name']:
                print 'Duplicate address for %s found:' % reg_addr
                print '  %s' % str(previous_addresses[reg_addr]['name'])
                print '  %s' % str(register[1]['name'])
                exit(1)
            previous_addresses[reg_addr] = register[0]

    print json_file_path + ' seems fine.'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s json_file_path' % sys.argv[0]
        exit(1)

    validate(sys.argv[1])
