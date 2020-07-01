#! /bin/bash
# Usage:
# gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name

if [ "$1" == "-h" ]; then
    echo "Usage: gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name"
    echo "Readme at: https://github.com/maltimore/gridsearch_helper"
    exit 1
fi

if [[ $# < 4 ]]; then
	# $# holds the number of CL arguments
	# this if-branch is executed if we have less than 3 arguments
	echo "ERROR! Call entry.sh with 4 parameters: path/to/main.py taskrange_begin taskrange_end job_name!"
    echo "Usage: gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name"
    echo "Readme at: https://github.com/maltimore/gridsearch_helper"
	exit 1
fi

script_filepath=$(readlink -f "$0")
script_dir=$(dirname "$script_filepath")
python_main_file="$1"
taskrange_begin="$2"
taskrange_end="$3"
job_name="$4"

# get the full path to the python main file with readlink
python_main_file=$(readlink -f $python_main_file)
python_main_file_dir=$(dirname "$python_main_file")
output_dir=./outfiles/"$job_name"

# If the output directory already exists, warn and ask whether we should exit
if [ -d "$output_dir" ]; then
    echo ""
    echo "Output directory already exists. You likely started a gridsearch with the same name as a previous one."
    echo "If you continue with this name for the gridsearch, the output files are going to be written into the existing directory."
    echo "Continue with this name for the gridsearch? [y/N]"
    read answer
    if [ "$answer" != "y" ]; then
        echo "Exiting, no gridsearch started"
        exit 1
    fi
fi

# make output directory
mkdir --parents "$output_dir"

# copy parameters file into output directory
cp "$python_main_file_dir"/parameters.yaml "$output_dir"/parameters.yaml

# Clear text output directory? (Ask only if it exists)
if [ -d "./textoutput/$job_name" ]; then
    echo ""
    echo "There is already a stdin/stderr directory at the location where we would put the stdin/stdout files for this new grisearch."
    echo "If the stdin/stderr files from the previous gridsearch are not removed, the ones from this one will be appended to the old ones."
    echo "If the previous gridsearch is still running, there is a chance that some of its jobs will crash if you temporarily remove the directory."
	echo "Shall I remove and re-create the textoutput folder? [y/n] (default: y)"
    read answer
    if [ "$answer" == "y" ] || [ "$answer" == "" ]; then
        echo "Clearing.."
        rm -rf ./textoutput/"$job_name"
    fi
fi

# if textoutput directory doesn't exist, create it
if [ ! -d "./textoutput/$job_name" ]; then
    echo ""
	echo "Creating textoutput directory textoutput"
	mkdir --parents ./textoutput/"$job_name"
fi

# start the actual jobs via the qsub command. We pass here the SGE_entry.sh script as the
# script that should be executed by qsub
qsub -cwd -N "$job_name" -t "$taskrange_begin"-"$taskrange_end" "$script_dir"/SGE_entry.sh "$script_dir" "$python_main_file_dir"
