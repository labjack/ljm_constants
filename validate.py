"""validate.py

Verifies that ljm_constants.json is not obviously invalid.
"""
import sys
import ljmmm

def validate(json_file_path):
    """Validates json_file_path as ljm constants JSON. Exits with non-zero on error."""
    print ('Checking JSON file...')
    try:
        json_map = ljmmm.get_device_modbus_maps(
            json_file_path,
            expand_names=True,
            inc_orig=True
        )

    except Exception as e:
        print ('[ERROR] JSON file registers could not be parsed. (' + str(e) + ')')
        exit(1)

    try:
        errors = ljmmm.get_errors(json_file_path)
    except Exception as e:
        print ('[ERROR] JSON file errors could not be parsed. (' + str(e) + ')')
        exit(1)

    err_msgs = []

    print 'Checking register map duplicates and streamable validity...'
    # Track all register names so we do not throw the same error twice for a
    # register (if the register is used with multiple devices)
    all_names = []
    for device in json_map:
        previous_names = []
        previous_addresses = {}
        device_registers = json_map[device]

        for register in device_registers:
            unresolved = register[0]
            resolved = register[1]
            if \
                'streamable' in unresolved and \
                unresolved['streamable'] and \
                not resolved['read']:
                    err_msgs.append(
                        "Register is streamable but not readable: %s" % (
                            resolved['name']
                        )
                    )

            reg_name = resolved['name']

            if reg_name in previous_names:
                err_msgs.append('Duplicate entries for %s found.' % reg_name)
            previous_names.append(reg_name)

            reg_addr = resolved['address']
            if reg_addr in previous_addresses and previous_addresses[reg_addr]['name'] != unresolved['name']:
                err_msgs.append(
                    'Duplicate address for %s found:\n'
                    '  %s\n'
                    '  %s' % (
                        reg_addr,
                        str(previous_addresses[reg_addr]['name']),
                        str(resolved['name'])
                    )
                )
            previous_addresses[reg_addr] = unresolved

            if resolved.has_key('description') and \
                len(resolved['description']) == 0 and \
                reg_name not in all_names:
                    err_msgs.append(
                        'No register description for: %s\n'
                        % str(reg_name)
                    )
            elif not resolved.has_key('description') and \
                reg_name not in all_names:
                err_msgs.append(
                        'No register description field for: %s\n'
                        % str(reg_name)
                    )
            all_names.append(reg_name)

    print ('Checking error duplicates...')
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
        print ('Duplicate errors:')
        for err in range(0, len(dup_ierrs)):
            print ('  ' + str(dup_ierrs[err]['error']))
        err_msgs.append('Duplication errors were found (see above)')

    for err in err_msgs:
        print (err)

    if len(err_msgs) != 0:
        exit(1)

    print (json_file_path + ' seems fine.')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ('Usage: %s json_file_path' % sys.argv[0])
        exit(1)

    validate(sys.argv[1])
