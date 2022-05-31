"""save_changes.py

Verifies that ljm_constants.json using validate.py, git commits all, and
pushes to origin.
"""
import os
import subprocess
import sys
from os import path

import validate

def save_changes(commit_message):
    cwd = os.chdir(path.dirname(path.abspath(__file__)))
    subprocess.call([sys.executable,'ljmmm_test.py'], cwd=cwd)
        
    constants_repo_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(constants_repo_dir, 'LabJack', 'LJM', 'ljm_constants.json')
    validate.validate(json_file_path)

    startup_configs_file_path = os.path.join(constants_repo_dir, 'LabJack', 'LJM', 'ljm_startup_configs.json')
    validate.validate(startup_configs_file_path, raw_only=False)

    subprocess.call([sys.executable,'generate_c_header.py'], cwd=cwd)

    print 'Saving to Git repository...'

    # Move to the repo
    os.chdir(constants_repo_dir)

    subprocess.check_call('git pull', shell=True, cwd=cwd)
    subprocess.call('git commit -a -m %s' % commit_message, shell=True, cwd=cwd)
    subprocess.call('git push', shell=True, cwd=cwd)

    print 'Finished!'

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print 'Too many args. Commit message may be arg 0.'
        sys.exit(1)

    commit_message = "Incremental JSON update."
    if len(sys.argv) == 2:
        commit_message = sys.argv[1]

    save_changes(commit_message)

