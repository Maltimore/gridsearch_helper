#!/usr/bin/env python
import sys
import os
import argparse
import shutil
from ruamel.yaml import YAML
import pathlib
import copy

yaml = YAML()

import util

parser = argparse.ArgumentParser()
parser.add_argument('--launch_script',
                    type=str,
                    help=(
                        'Path to the script that should be run. '
                        'You should take the example script at SGE/SGE_entry.sh and modify it to your needs. '
                        'You can then place your modified copy of SGE_entry.sh (possibly renamed) and place it '
                        'somewhere on your system. Then, provide the path to that script here.'
                    ))
parser.add_argument('--path',
                    type=str,
                    help='Output directory.')
parser.add_argument('--params_path',
                    type=str,
                    default='src/parameters.yaml',
                    help='Optional. Default is ./src/parameters.yaml. Path to parameters file.')
parser.add_argument('--taskrange_begin',
                    type=int,
                    default=1,
                    help='Optional. Default is 1.')
parser.add_argument('--taskrange_end',
                    type=int,
                    default=1,
                    help=(
                        'Optional. Default is 1. '
                        'If (taskrange_end - taskrange_begin) == 1, this will be a normal (non-gridsearch) job.'
                    ))
parser.add_argument('--job_name',
                    default=None,
                    type=str,
                    help='Optional. If you do not provide a job name, the output directory is taken as the job name.')
args = parser.parse_args()
output_path = os.path.abspath(args.path)
if args.job_name is None:
    job_name = os.path.basename(output_path)
    print(f'Job name set to {job_name}')

if os.path.exists(output_path):
    print(f"Output directory {output_path} already exists, "
          "should we continue?")
    if not input('[y to continue]') == 'y':
        sys.exit('Ok, no job started')

if not os.path.exists(output_path):
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path, 'stdin_and_out'))


gridsearch = True if args.taskrange_end - args.taskrange_begin > 0 else False
# copy the params file to the output folder, regardless of whether this is a
# gridsearch or not. If it is a gridsearch, we will later copy appropriate
# params files into each output directory (for each job)
shutil.copyfile(args.params_path, os.path.join(output_path, 'parameters.yaml'))

if gridsearch:
    params = yaml.load(pathlib.Path(args.params_path))
    if not os.path.exists(os.path.join(output_path, 'job_outputs')):
        os.makedirs(os.path.join(output_path, 'job_outputs'))

    for job_idx in range(args.taskrange_begin, args.taskrange_end + 1):
        job_output_dir = os.path.join(output_path, 'job_outputs', str(job_idx).zfill(5))
        if not os.path.exists(job_output_dir):
            os.makedirs(job_output_dir)
        job_params = util.assign_hyperparams(job_idx, copy.deepcopy(params))
        yaml.dump(job_params, pathlib.Path(job_output_dir, 'parameters.yaml'))


repository_copy_path = os.path.join(output_path, 'repository')
if not os.path.exists(repository_copy_path):
    print(f'Making repository directory {repository_copy_path}')
    os.makedirs(repository_copy_path)

    print('Creating archive of git repository, including tracked changes')
    git_status_clean = not os.system('git diff-index --quiet HEAD')
    if not git_status_clean:
        # git status is dirty, create archive from stash
        os.system(f'git archive `git stash create` -o {output_path}/temporary_git_stash_archive.tar')
    else:
        # git status is clean, create archive from HEAD
        os.system(f'git archive HEAD -o {output_path}/temporary_git_stash_archive.tar')
    print(f'Unpacking git archive to {repository_copy_path}')
    os.system(f'tar -xf {output_path}/temporary_git_stash_archive.tar -C {repository_copy_path}')
    os.system(f'rm {output_path}/temporary_git_stash_archive.tar')

print(f'Switching to repository directory {repository_copy_path}')
os.chdir(repository_copy_path)
print(f'Now in {os.getcwd()}')

qsub_command = (
    'qsub ' +
    '-cwd ' +
    f'-N {job_name} ' +
    f'-t {args.taskrange_begin}-{args.taskrange_end} ' +
    f'{args.launch_script} '
)
qsub_command += 'is_gridsearch ' if gridsearch else 'is_not_gridsearch '
qsub_command += f'{output_path}'

print('Running the following qsub command now')
print(qsub_command)
os.system(qsub_command)
