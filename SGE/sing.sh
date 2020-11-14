echo "Hello from sing.sh"

# add .bin and programs to PATH
export PATH="$HOME"/.local/bin:"$HOME"/programs/:$PATH
export PYTHONPATH="$HOME"/.local/bin:$PYTHONPATH

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

python src/main.py --path="$1"
