#! /bin/bash
#$ -V
#$ -l h_vmem=5G
#$ -l h_rt=04:00:00
#$ -binding linear:2
#$ -l h="!node05"
#$ -l h="!node08"
#$ -l h="!node12"
#$ -l h="!node29"
#$ -o ../stdin_and_out/$TASK_ID.out
#$ -e ../stdin_and_out/$TASK_ID.error

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

if [ docker image inspect malte/rllib >/dev/null 2>&1 == 1 ]; then
    echo docker image is not in the registry on this node, loading it from tar file
    docker image load --input /home/malte/repos/proteinfolding/docker/malte_rllib_docker_image.tar
fi

echo Now calling docker
docker run --shm-size=2G --mount src="$HOME",target=/home/malte,type=bind malte/rllib python /home/malte/repos/proteinfolding/src/main.py --path=$output_path --params_path=$params_path
#singularity exec ~/ray_latest.sif ./src/sing.sh $output_path $params_path
