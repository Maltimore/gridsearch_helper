#! /bin/bash
#$ -cwd
#$ -V
#$ -l h_vmem=20G
#$ -l s_rt=00:40:00
#$ -l h_rt=00:30:00
#$ -o ./textoutput/$JOB_NAME/$TASK_ID.out
#$ -e ./textoutput/$JOB_NAME/$TASK_ID.error

# $1 is the directory that we're supposed to be in. We get it passed as a cli argument,
# because we're not *actually* in this directory. Qsub puts this file into another directory.
python "$1"/python_entry.py
