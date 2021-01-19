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

array_job="$1"
if [ "$array_job" == "0" ]; then
    echo This is a normal \(non-array\)-job
    output_path="$2"
    export ARRAY_JOB=1
else
    echo This is an array job
    output_path="$2"/job_outputs/"$(printf %05d "$SGE_TASK_ID")"
    export ARRAY_JOB=0
fi
echo The output path is "$output_path"
params_path=$output_path/parameters.yaml

export OUTPUT_PATH=$output_path
export PARAMS_PATH=$params_path

echo Current working directory: "$(pwd)"
echo Hostname: "$(hostname)"


python <<HEREDOC
import datetime
start_time = datetime.datetime.now()
print(f"SGE_entry start time: {start_time}")
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
    "start_time": str(start_time),
    "git_hash": get_git_info()["git_hash"],
    "git_status": get_git_info()["git_status"],
    "array_job": True if os.environ['ARRAY_JOB'] == 1 else False,
    "hostname": platform.uname()[1],
    "run_finished": False,
    "task_id": int(os.environ['SGE_TASK_ID']),
}
yaml.dump(run_info, pathlib.Path(os.environ['OUTPUT_PATH'], 'run_info.yaml'))
HEREDOC

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
# starting here you can put the commands you would like to run

python src/main.py --path "$output_path" --params_path "$params_path"


# finish the job by putting the end time into the run_info.yaml
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
python <<HEREDOC
import datetime
from ruamel.yaml import YAML
import pathlib
import os

yaml = YAML()
run_info = yaml.load(pathlib.Path(os.environ['OUTPUT_PATH'], 'run_info.yaml'))
end_time = datetime.datetime.now()
run_time_seconds = (end_time - datetime.datetime.strptime(run_info['start_time'], '%Y-%m-%d %H:%M:%S.%f')).seconds
print(f"End time: {end_time}")
print(f"Run time (seconds): {run_time_seconds}", flush=True)

run_info["end_time"] = str(end_time)
run_info["run_time_seconds"] = run_time_seconds
run_info["run_finished"] = True
yaml.dump(run_info, pathlib.Path(os.environ['OUTPUT_PATH'], 'run_info.yaml'))
HEREDOC
