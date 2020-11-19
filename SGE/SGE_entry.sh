#! /bin/bash
#$ -V
#$ -l h_vmem=4G
#$ -l h_rt=02:00:00
#$ -binding linear:2
#$ -l h='*&!node11'
#$ -o ../stdin_and_out/$TASK_ID.out
#$ -e ../stdin_and_out/$TASK_ID.error

# EXPLANATION OF SOME PARAMETERS
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

echo Now in SGE_entry.sh

gridsearch="$1"
if [ $gridsearch == "is_not_gridsearch" ]; then
    output_path="$2"
else
    echo This is a gridsearch
    output_path="$2"/job_outputs/`printf "%05d" $SGE_TASK_ID`
fi
echo The output path is $output_path
params_path=$output_path/parameters.yaml

echo Current working directory: `pwd`
echo Hostname: `hostname`

#if [ docker image inspect malte/rllib >/dev/null 2>&1 == 0 ]; then
#    echo Did not need to load the docker image, because it is in the registry on this node
#else
#    echo Docker image is not in the registry on this node, need to load it from tar file.
#    echo However, we will first sleep a random amount of time to see if some other job is going to load it first
#    /bin/sleep   `/usr/bin/expr $RANDOM % 300`
#    if [ docker image inspect malte/rllib >/dev/null 2>&1 == 0 ]; then
#        echo Image has been loaded in the meantime
#    else
#        echo Loading image now
#        docker image load --input /home/malte/repos/proteinfolding/docker/malte_rllib_docker_image.tar
#    fi
#fi

#docker run --shm-size=2G --rm --mount src="$HOME",target=/home/malte,type=bind malte/rllib python /home/malte/repos/proteinfolding/src/main.py --path=$output_path --params_path=$params_path
echo Now calling singularity
singularity exec --net --fakeroot -B /home/malte:/home/malte ~/ray_latest.sif ./src/sing.sh $output_path $params_path
