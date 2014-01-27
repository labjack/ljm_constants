import json
import os
import subprocess

print 'Checking JSON file...'
json_file_path = os.path.join('LabJack', 'LJM', 'ljm_constants.json')
with open(json_file_path) as f:
    try:
        json.load(f)
    except:
        print '[ERROR] JSON file could not be parsed. Please check.'
        exit(1)

print 'Saving to Git repository...'
subprocess.check_call('git pull', shell=True)
subprocess.check_call('git commit -a -m "Incremental JSON update."', shell=True)
subprocess.check_call('git push', shell=True)
print 'Finished!'
