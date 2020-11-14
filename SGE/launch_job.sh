#! /bin/bash
# Usage:
# launch_job.sh path/to/your_script.sh output_path [job_name]

#if [ "$1" == "-h" ]; then
#    echo "Usage: gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name"
#    echo "Readme at: https://github.com/maltimore/gridsearch_helper"
#    exit 1
#fi

#if [[ $# < 4 ]]; then
#	# $# holds the number of CL arguments
#	# this if-branch is executed if we have less than 3 arguments
#	echo "ERROR! Call entry.sh with 4 parameters: path/to/main.py taskrange_begin taskrange_end job_name!"
#    echo "Usage: gridsearch_entry.sh path/to/main.py taskrange_begin taskrange_end job_name"
#    echo "Readme at: https://github.com/maltimore/gridsearch_helper"
#	exit 1
#fi

script_to_execute="$1"
output_path="$2"
#this_script_filepath=$(readlink -f "$0")
#this_script_dir=$(dirname "$this_script_filepath")
if [[ $# == 3 ]]; then
    job_name="$3"
fi


# If the output directory already exists, warn and ask whether we should exit
if [ -d "$output_path" ]; then
    echo ""
    echo "Output directory already exists."
    echo "Continue? [y/N]"
    read answer
    if [ "$answer" != "y" ]; then
        echo "Exiting, no job started"
        exit 1
    fi
fi

# make output directory
mkdir --parents "$output_path"

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

# copy repository (including changes) to the output directory
if [ ! -d $output_path/repository ]; then
    git archive `git stash create` -o $output_path/temporary_git_stash_archive.tar
    tar -xf $output_path/temporary_git_stash_archive.tar -C $output_path/repository
    rm $output_path/temporary_git_stash_archive.tar

cd $output_path/repository

# start the actual jobs via the qsub command. We pass here the SGE_entry.sh script as the
# script that should be executed by qsub
# -N is for the name
qsub -cwd -N "$job_name" $script_to_execute $output_path
