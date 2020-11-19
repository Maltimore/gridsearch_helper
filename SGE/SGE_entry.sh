#! /bin/bash
#$ -V
#$ -l h_vmem=4G
#$ -l h_rt=02:00:00
#$ -binding linear:2
#$ -l h='*&!node11'
#$ -o ../stdin_and_out/$TASK_ID.out
#$ -e ../stdin_and_out/$TASK_ID.error

########################################################################
# YOU SHOULD COPY AND MODIFY THIS FILE TO SUIT YOUR NEEDS.
# I RECOMMEND TO ONLY MODIFY THE PART BETWEEN THE COMMENTED LINES
########################################################################

# EXPLANATION OF SOME PARAMETERS
# -cwd : run job in the current directory (has no effect here! needs to be passed in the calling script)
# -V : take over currently active environment variables for the job
# -l h_vmem=50G : amount of RAM to reserve for the job
# -l h_rt=hour:minute:seconds : Hard runtime limit. After the specified hard runtime limit, Sun Grid Engine aborts the job using the SIGKILL signal.
# -l s_rt=hour:minute:seconds : Soft limit is reached, Sun Grid Engine warns the job by sending the job the SIGUSR1 signal.
# -l cuda=1  : reserve a GPU
# -binding linear:3  : use 3 cpu cores
# -l h=nodeXX  : run on nodeXX
# -l h=!nodeXX  : exclude nodeXX
# -o /path/ : where to put stdout
# -e /path/ : where to put sderr

# Jobs that do not specify an elapsed time limit inherit a system default. The default is necessary for the Advance Reservation system to assure resource availability. 

echo Now in SGE_entry.sh

gridsearch="$1"
if [ $gridsearch == "is_not_gridsearch" ]; then
    output_path="$2"
else
    echo This is a gridsearch
    output_path="$2"/job_outputs/`printf "%05d" $SGE_TASK_ID`
fi
echo The output path is $output_path
params_path=$output_path/parameters.yaml

echo Current working directory: `pwd`
echo Hostname: `hostname`


python <<HEREDOC
import time
start_time = time.time()
print("Start time: {}".format(
    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time))))
import os
import platform
import subprocess
import warnings
from ruamel.yaml import YAML
import pathlib

yaml = YAML()


def get_git_info():
    try:
        return_dict = {
            "git_hash": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip('\n'),
            "git_status":  subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8'),
        }
    except Exception:
        warnings.warn('\nWarning! Failed to get git revision hash!\n')
        return_dict = {
            "git_hash": "failed_to_get",
            "git_status": "failed_to_get"
        }
    return return_dict


run_info = {
    "start_time": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time)),
    "git_hash": get_git_info()["git_hash"],
    "git_status": get_git_info()["git_status"],
    "gridsearch": True,
    "hostname": platform.uname()[1],
    "run_finished": False,
    "task_id": int(os.environ['SGE_TASK_ID']),
}
yaml.dump(run_info, pathlib.Path('$output_path', 'program_state.yaml'))
HEREDOC

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
# starting here you can put the commands you would like to run

python src/main.py $output_path $params_path


# finish the job by putting the end time into the program_state.yaml
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
python <<HEREDOC
import time
from ruamel.yaml import YAML
import pathlib

yaml = YAML()
run_info = yaml.load(pathlib.Path('$output_path', 'program_state.yaml'))
end_time = time.time()
run_time = end_time - run_info['start_time']
print("End time: {}".format(
    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(end_time))))
print("Run time (seconds): {}".format(run_time), flush=True)

run_info["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(end_time))
run_info["run_time"] = time.strftime('%H:%M:%S', time.gmtime(run_time))
run_info["run_finished"] = True
yaml.dump(run_info, pathlib.Path('$output_path', 'program_state.yaml'))
HEREDOC
