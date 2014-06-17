import json
import os
import subprocess
import sys

import ljmmm

if len(sys.argv) > 2:
    print 'Too many args. Commit message may be arg 0.'
    sys.exit(1)
    
commit_message = "Incremental JSON update."
if len(sys.argv) == 2:
    commit_message = sys.argv[1]

print 'Checking JSON file...'
json_file_path = os.path.join('MANUAL_LJM_CONSTANTS', 'LabJack', 'LJM', 'ljm_constants.json')
try:
    json_map = ljmmm.get_device_modbus_maps(json_file_path)
except Exception as e:
    print '[ERROR] JSON file could not be parsed. Please check. (' + str(e) + ')'
    exit(1)

print 'Checking register map duplicates...'
for device in json_map:
    previous_names = []
    previous_addresses = []
    device_registers = json_map[device]
    
    for register in device_registers:
        reg_name = register['name']
        
        if reg_name in previous_names:
            print 'Duplicate entries for %s found.' % reg_name
            exit(1)
        previous_names.append(reg_name)

# print "HERE"
gitCommand = 'cd MANUAL_LJM_CONSTANTS && git '
gitFooter = ' && cd ..'
# p = subprocess.Popen("pwd", stdout=subprocess.PIPE)
# result = p.communicate()[0]
# print result
print 'Saving to Git repository...'
subprocess.check_call(gitCommand + 'pull' + gitFooter, shell=True)
subprocess.call((gitCommand + 'commit -a -m "%s"' + gitFooter) % commit_message, shell=True)
subprocess.call(gitCommand + 'push' + gitFooter, shell=True)
print 'Finished!'
