#! /bin/bash
#$ -V
#$ -l h_vmem=4G
#$ -l h_rt=02:00:00
#$ -binding linear:2
#$ -o ../stdin_and_out/$TASK_ID.out
#$ -e ../stdin_and_out/$TASK_ID.error

# You should copy and modify this file to suit your needs.
# I recommend to only modify the part almost all the way at the bottom where it
# is indicated you should change.

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

# Jobs that do not specify an elapsed time limit inherit a system default. The
# default is necessary for the Advance Reservation system to assure resource
# availability.

echo "Now in SGE_entry.sh"

ARRAY_JOB="$(( SGE_TASK_LAST > 1 ))"
if (( ARRAY_JOB )); then
    OUTPUT_PATH+="/job_outputs/$(printf %05d "$SGE_TASK_ID")"
fi
echo "The output path is ${OUTPUT_PATH}"
mkdir -p "$OUTPUT_PATH"

export OUTPUT_PATH
export ARRAY_JOB
export PARAMS_PATH="${OUTPUT_PATH}/parameters.yaml"
export RANDOM_SEED="$RANDOM"

echo "Current working directory: $(pwd)"
echo "Hostname: $(hostname)"


# gather information about the current environment and save it to run_info.yaml
# QLAUNCH_SCRIPT is a variable created in the qlaunch file and it points to the
# location of the qlaunch file.
"$QLAUNCH_SCRIPT" --action setup


# starting here you can put the commands you would like to run. You should use the pre-defined variables
# "$OUTPUT_PATH" "$PARAMS_PATH" (and "$RANDOM_SEED" if you need to set a seed)
python path/to/main.py "$OUTPUT_PATH" "$PARAMS_PATH" "$RANDOM_SEED"


# finish the job by putting the end time into the run_info.yaml
"$QLAUNCH_SCRIPT" --action cleanup
