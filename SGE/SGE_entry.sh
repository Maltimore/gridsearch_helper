#! /bin/bash
#$ -V
#$ -l h_vmem=20G
#$ -l h_rt=02:00:00
#$ -o ./textoutput/$JOB_NAME/$TASK_ID.out
#$ -e ./textoutput/$JOB_NAME/$TASK_ID.error

# EXPLANATION SOME PARAMETERS
# -cwd : run job in the current directory
# -V : take over currently active environment variables for the job
# -l h_vmem=50G : amount of RAM to reserve for the job
# -l h_rt=hour:minute:seconds : Hard runtime limit. After the specified hard runtime limit, Sun Grid Engine aborts the job using the SIGKILL signal.
# -l s_rt=hour:minute:seconds : Soft limit is reached, Sun Grid Engine warns the job by sending the job the SIGUSR1 signal.
# -o /path/ : where to put stdout
# -e /path/ : where to put sderr

# Jobs that do not specify an elapsed time limit inherit a system default. The default is necessary for the Advance Reservation system to assure resource availability. 

echo "hello from SGE_entry.sh"
echo "$0"
echo "$1"
echo "$2"
singularity exec ~/ubuntu_20.04.sif "$1"/sing.sh "$1" "$2"
