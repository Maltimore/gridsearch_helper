#! /bin/bash
#SBATCH --mem=999M

echo "Now in SLURM_entry.sh"

echo "Current working directory: $(pwd)"
echo "Hostname: $(hostname)"

OUTPUT_PATH+="/job_outputs/$(printf %05d "$SLURM_ARRAY_TASK_ID")"
echo "The output path is ${OUTPUT_PATH}"

PARAMS_PATH="${OUTPUT_PATH}/parameters.yaml"
export RANDOM_SEED="$RANDOM"

# gather information about the current environment and save it to run_info.yaml
"$LAUNCH_SCRIPT" --action setup  --path="${OUTPUT_PATH}"

# starting here you can put the commands you would like to run


# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$($HOME'/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f $HOME"/miniconda3/etc/profile.d/conda.sh" ]; then
        . $HOME"/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH=$HOME"/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
conda activate structnet
echo $(date) "conda activate is done"

python scripts/main.py --path="${OUTPUT_PATH}" --params_path="${PARAMS_PATH}" --random_seed="${RANDOM_SEED}" --action=train_e2e


# finish the job by putting the end time into the run_info.yaml
"$LAUNCH_SCRIPT" --action cleanup  --path="${OUTPUT_PATH}"
