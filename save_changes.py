import json
import os
import subprocess

import ljmmm

print 'Checking JSON file...'
json_file_path = os.path.join('LabJack', 'LJM', 'ljm_constants.json')
try:
    ljmmm.get_raw_registers_data(json_file_path)
except Exception as e:
    print '[ERROR] JSON file could not be parsed. Please check. (' + str(e) + ')'
    exit(1)

print 'Saving to Git repository...'
subprocess.check_call('git pull', shell=True)
subprocess.call('git commit -a -m "Incremental JSON update."', shell=True)
subprocess.call('git push', shell=True)
print 'Finished!'
