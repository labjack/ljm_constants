"""save_changes.py

Verifies that ljm_constants.json using validate.py, git commits all, and
pushes to origin.
"""
import os
import subprocess
import sys

import validate

subprocess.call('python3 ljmmm_test.py')

if len(sys.argv) > 2:
    print('Too many args. Commit message may be arg 0.')
    sys.exit(1)
    
commit_message = "Incremental JSON update."
if len(sys.argv) == 2:
    commit_message = sys.argv[1]
    
constants_repo_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(constants_repo_dir, 'LabJack', 'LJM', 'ljm_constants.json')
validate.validate(json_file_path)

json_file_path = os.path.join(constants_repo_dir, 'LabJack', 'LJM', 'ljm_startup_configs.json')
validate.validate(json_file_path)

subprocess.call('python3 generate_c_header.py')

print('Saving to Git repository...')

# Move to the repo
os.chdir(constants_repo_dir)

subprocess.check_call('git pull', shell=True)
subprocess.call('git commit -a -m "%s"' % commit_message, shell=True)
subprocess.call('git push', shell=True)

print('Finished!')
