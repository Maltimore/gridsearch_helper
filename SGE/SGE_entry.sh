#! /bin/bash
#$ -V
#$ -l h_vmem=5G
#$ -l h_rt=04:00:00
#$ -binding linear:3
#$ -l h="!node08"
#$ -o ./textoutput/$JOB_NAME/$TASK_ID.out
#$ -e ./textoutput/$JOB_NAME/$TASK_ID.error

# EXPLANATION SOME PARAMETERS
# -cwd : run job in the current directory (has no effect here! needs to be passed in the calling script)
# -V : take over currently active environment variables for the job
# -l h_vmem=50G : amount of RAM to reserve for the job
# -l h_rt=hour:minute:seconds : Hard runtime limit. After the specified hard runtime limit, Sun Grid Engine aborts the job using the SIGKILL signal.
# -l s_rt=hour:minute:seconds : Soft limit is reached, Sun Grid Engine warns the job by sending the job the SIGUSR1 signal.
# -l cuda=1  : reserve a GPU
# -binding linear:3  : use 3 cpu cores
# -l h=nodeXX  : run on nodeXX
# -l h=!nodeXX  : exclude nodeXX
# -o /path/ : where to put stdout
# -e /path/ : where to put sderr

# Jobs that do not specify an elapsed time limit inherit a system default. The default is necessary for the Advance Reservation system to assure resource availability. 

echo "In SGE_entry.sh"
echo Hostname: `hostname`
echo Calling script: "$0"
echo gridsearch/SGE folder location: "$1"
echo Path to main file folder: "$2"
singularity exec ~/ray_latest.sif "$1"/sing.sh "$1" "$2"
