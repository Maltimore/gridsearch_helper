#! /bin/bash

echo $(date) "Now in SLURM_entry.sh"

echo $(date) "Current working directory: $(pwd)"
echo $(date) "Hostname: $(hostname)"

# DO NOT MESS WITH THE VARIABLES RANDOM_SEED AND OUTPUT_PATH
export RANDOM_SEED="$RANDOM"
# we are accessing here the OUTPUT_PATH variable that is set in slurmlaunch
# and modify if with the info of the current job
OUTPUT_PATH+="/job_outputs/$(printf %05d "$SLURM_ARRAY_TASK_ID")"
echo $(date) "The output path is ${OUTPUT_PATH}"

PARAMS_PATH="${OUTPUT_PATH}/parameters.yaml"
export RANDOM_SEED="$RANDOM"

# gather information about the current environment and save it to run_info.yaml
echo $(date) running launch script
"$LAUNCH_SCRIPT" --action setup  --output-path="${OUTPUT_PATH}"
echo $(date) Starting main program

########################################################################################################################
# here you can put the commands you would like to run
SCRIPT='scripts/my_example_script.py'
echo $(date) Running ${SCRIPT}
python ${SCRIPT} --output_path="${OUTPUT_PATH}" --params_path="${PARAMS_PATH}" --random_seed="${RANDOM_SEED}"
########################################################################################################################

# finish the job by putting the end time into the run_info.yaml
echo $(date) running cleanup script
"$LAUNCH_SCRIPT" --action cleanup  --output-path="${OUTPUT_PATH}"
