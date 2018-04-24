#! /bin/bash

if [[ $# < 3 ]]; then
	# $# holds the number of CL arguments
	# this if-branch is executed if we have less than 3 arguments
	echo "ERROR Call qsub.sh with three parameters: taskrange_begin taskrange_end job_name!"
	exit 1
fi

script_filepath=$(readlink -f "$0")
script_dir=$(dirname "$script_filepath")
taskrange_begin="$1"
taskrange_end="$2"
job_name="$3"


# Clear text output directory?
if [ -d "./textoutput/$job_name" ]; then
    echo "Shall I clear the folders with output and error text? [y/n]"
    read answer

    if [ "$answer" == "y" ] || [ "$answer" == "" ]; then
        echo "Clearing.."
        rm -rf ./textoutput/"$job_name"
    fi
fi

# if textoutput directory doesn't exist, create
if [ ! -d "./textoutput/$job_name" ]; then
	echo "Creating textoutput directory textoutput"
	mkdir -p ./textoutput/"$job_name"
fi

qsub -N "$job_name" -t "$taskrange_begin"-"$taskrange_end" "$script_dir"/SGE_entry.sh "$script_dir"
