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
        print '[ERROR] JSON file registers could not be parsed. (' + str(e) + ')'
        exit(1)

    try:
        errors = ljmmm.get_errors(json_file_path)
    except Exception as e:
        print '[ERROR] JSON file errors could not be parsed. (' + str(e) + ')'
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

    print 'Checking error duplicates...'
    dup_ierrs = []
    dup_jerrs = []
    for i_it in range(0, len(errors)):
        for j_it in range(i_it + 1, len(errors)):
            ierr = errors[i_it]
            jerr = errors[j_it]
            if ierr['error'] == jerr['error'] and ierr['error'] not in dup_ierrs:
                dup_ierrs.append(ierr)
                dup_jerrs.append(jerr)

    if dup_ierrs:
        print 'Duplicate errors:'
        for err in range(0, len(dup_ierrs)):
            print '  ' + str(dup_ierrs[err]['error'])
        exit(1)

    print json_file_path + ' seems fine.'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s json_file_path' % sys.argv[0]
        exit(1)

    validate(sys.argv[1])
