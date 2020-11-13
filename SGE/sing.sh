echo "Hello from sing.sh"
. ~/.reduced_bashrc
conda activate py38

# $1 is the directory that this script is in. We get it passed as a cli argument by the calling script,
# because the SGE_entry script is not *actually* in this directory. Qsub puts this file into another directory.
# $2 is the directory that the main.py file of the program we're supposed to run is in
python "$1"/python_entry.py "$2"
