#! /bin/bash
# Usage:
# gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name

if [[ $# < 4 ]]; then
	# $# holds the number of CL arguments
	# this if-branch is executed if we have less than 3 arguments
	echo "ERROR! Call entry.sh with 4 parameters: path/to/main.py taskrange_begin taskrange_end job_name!"
	exit 1
fi

script_filepath=$(readlink -f "$0")
script_dir=$(dirname "$script_filepath")
python_main_file="$1"
taskrange_begin="$2"
taskrange_end="$3"
job_name="$4"

# get the full path to directory of the python main file
python_main_file=$(readlink -f $python_main_file)
python_main_file_dir=$(dirname "$python_main_file")

# Clear text output directory? (Ask only if it exists)
if [ -d "./textoutput/$job_name" ]; then
	echo "Shall I clear the folders with output and error text? [y/n] (default: y)"
    read answer

    if [ "$answer" == "y" ] || [ "$answer" == "" ]; then
        echo "Clearing.."
        rm -rf ./textoutput/"$job_name"
    fi
fi

# if textoutput directory doesn't exist, create it
if [ ! -d "./textoutput/$job_name" ]; then
	echo "Creating textoutput directory textoutput"
	mkdir -p ./textoutput/"$job_name"
fi

# start the actual jobs via the qsub command. We pass here the SGE_entry.sh script as the
# script that should be executed by qsub
qsub -cwd -N "$job_name" -t "$taskrange_begin"-"$taskrange_end" "$script_dir"/SGE_entry.sh "$script_dir" "$python_main_file_dir"
