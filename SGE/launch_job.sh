#! /bin/bash
# Usage:
# launch_job.sh path/to/your/SGE_entry.sh job_name output_path

if [ "$1" == "-h" ]; then
    echo "Usage: launch_job.sh path/to/your/SGE_entry.sh job_name output_path"
    echo "Readme at: https://github.com/maltimore/gridsearch_helper"
    exit 1
fi

if [[ $# < 3 ]]; then
    echo You passed too few arguments, do launch_job.sh -h to see usage
    exit 1
fi

script_to_execute="$1"
echo Script to execute with qsub: $script_to_execute
job_name="$2"
echo Job name: $job_name
# use readlink to get the absolute path
output_path=`readlink -f "$3"`
echo Output path: $output_path

# If the output directory already exists, warn and ask whether we should exit
if [ -d "$output_path" ]; then
    echo ""
    echo "Output directory $output_path already exists."
    echo "Continue? [y/N]"
    read answer
    if [ "$answer" != "y" ]; then
        echo "Exiting, no job started"
        exit 1
    fi
fi

# make output directory
mkdir --parents "$output_path"

# copy git repository (including changes) to the output directory such that we can run from there
repository_copy_path=$output_path/repository
if [ ! -d $repository_copy_path ]; then
    echo Making repository directory $repository_copy_path
    mkdir $repository_copy_path
    # we need to find out whether git status is clean
    echo Creating archive of current git repository..
    git diff-index --quiet HEAD 
    # $? gets the status of the last command
    if [ $? == 1 ]; then
        # git status is dirty, create archive from stash
        git archive `git stash create` -o $output_path/temporary_git_stash_archive.tar
    else
        # git status is clean, create archive from HEAD
        git archive HEAD -o $output_path/temporary_git_stash_archive.tar
    fi

    echo Unpacking git archive to $repository_copy_path
    tar -xf $output_path/temporary_git_stash_archive.tar -C $repository_copy_path
    rm $output_path/temporary_git_stash_archive.tar
fi
echo Switching to repository directory $repository_copy_path
cd $repository_copy_path
echo Now in directory `pwd`

# start the actual jobs via the qsub command. We pass here the SGE_entry.sh script as the
# script that should be executed by qsub
# -N is for the job name
echo Running qsub command now
qsub -cwd -N "$job_name" -o "$output_path"/stdout -e "$output_path"/stderr "$script_to_execute" "$output_path"
