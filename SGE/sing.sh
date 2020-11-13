echo "Hello from sing.sh"

# add .bin and programs to PATH
export PATH="$HOME"/.local/bin:"$HOME"/programs/:$PATH
export PYTHONPATH="$HOME"/.local/bin:$PYTHONPATH
export EDITOR=vi

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$($HOME'/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f $HOME"/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/maltimore/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH=$HOME"/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate py38

# $1 is the directory that this script is in. We get it passed as a cli argument by the calling script,
# because the SGE_entry script is not *actually* in this directory. Qsub puts this file into another directory.
# $2 is the directory that the main.py file of the program we're supposed to run is in
echo "Calling $1/python_entry.py now"
python "$1"/python_entry.py "$2"
