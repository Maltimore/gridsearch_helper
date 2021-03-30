#!/usr/bin/env python
import sys
import os
import argparse
import shutil
from ruamel.yaml import YAML
import pathlib
import copy
import subprocess

yaml = YAML()

import util

parser = argparse.ArgumentParser()
parser.add_argument('--path',
                    type=str,
                    help='Output directory.')
parser.add_argument('--launch_script',
                    type=str,
                    default='cluster/SGE_entry.sh',
                    help=(
                        'Default is ./cluster/SGE_entry.sh. '
                        'Path to the script that should be run. '
                        'You should take the example script at SGE/SGE_entry.sh and modify it to your needs. '
                        'You can then place your modified copy of SGE_entry.sh (possibly renamed) and place it '
                        'somewhere on your system. Then, provide the path to that script here.'
                    ))
parser.add_argument('--params_path',
                    type=str,
                    default='src/parameters.yaml',
                    help='Default is ./src/parameters.yaml. Path to parameters file.')
parser.add_argument('--taskrange_begin',
                    type=int,
                    default=1,
                    help='Default is 1.')
parser.add_argument('--taskrange_end',
                    type=int,
                    default=1,
                    help=(
                        'Default is 1. '
                        'If (taskrange_end - taskrange_begin) == 1, this will be a normal (non-array) job.'
                    ))
parser.add_argument('--job_name',
                    default=None,
                    type=str,
                    help='Default is the output directory of --path as the job name.')
parser.add_argument('--node',
                    default=None,
                    type=str,
                    help=(
                        'Default is None. Set the node to run on. This setting will be passed directly to '
                        'qsub in the form of -l h=<node>. '
                        'If you don\'t set this, then the setting in your SGE_entry.sh will '
                        'be used. If you do not set that either, it is equivalent to \'*\'.'
                    ))
args = parser.parse_args()
args.path = os.path.abspath(args.path)
args.launch_script = os.path.abspath(args.launch_script)
args.params_path = os.path.abspath(args.params_path)
# job_name
if args.job_name is None:
    args.job_name = os.path.basename(args.path)
    print(f'Job name set to {args.job_name}')

if os.path.exists(args.path):
    print(f"Output directory {args.path} already exists, "
          "should we continue?")
    if not input('[y to continue]') == 'y':
        sys.exit('Ok, no job started')
else:
    os.makedirs(args.path)
if not os.path.exists(os.path.join(args.path, 'stdin_and_out')):
    os.makedirs(os.path.join(args.path, 'stdin_and_out'))


array_job = True if args.taskrange_end - args.taskrange_begin > 0 else False
# copy the params file to the output folder, regardless of whether this is an
# array-job or not. If it is an array-job, we will later copy appropriate
# params files into each output directory (for each job)
shutil.copyfile(args.params_path, os.path.join(args.path, 'parameters.yaml'))

if array_job:
    params = yaml.load(pathlib.Path(args.params_path))
    if not os.path.exists(os.path.join(args.path, 'job_outputs')):
        os.makedirs(os.path.join(args.path, 'job_outputs'))

    for job_idx in range(args.taskrange_begin, args.taskrange_end + 1):
        job_output_dir = os.path.join(args.path, 'job_outputs', str(job_idx).zfill(5))
        if not os.path.exists(job_output_dir):
            os.makedirs(job_output_dir)
        job_params = util.assign_hyperparams(job_idx, copy.deepcopy(params))
        yaml.dump(job_params, pathlib.Path(job_output_dir, 'parameters.yaml'))


repository_copy_path = os.path.join(args.path, 'repository')
if os.path.exists(repository_copy_path):
    print('There is already a (possibly old or incomplete) copy of the repository at the selected output path ' +
          repository_copy_path)
    answer = input('Delete the copy and re-create it? (y/n)')
    if answer == 'y':
        print(f'Ok, deleting directory at {repository_copy_path}')
        shutil.rmtree(repository_copy_path)
if not os.path.exists(repository_copy_path):
    # repository copy does not exist yet, create it
    print(f'Making repository directory {repository_copy_path}')
    os.makedirs(repository_copy_path)

    print('Creating archive of git repository, including tracked changes (but not not tracked changes)')
    # when the user is not in the git root directory and we perform git archive, only the contents
    # of the current directory are put into the archive
    # capture_output=True checks the stdout and stderr of a command
    # text=True transforms to proper text (utf-8 presumably)
    git_root_directory = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True
    ).stdout
    # rstrip removes whitespace from the end of the string (in our case, a newline character)
    git_root_directory = git_root_directory.rstrip()
    git_status_clean = not os.system('git diff-index --quiet HEAD')
    if not git_status_clean:
        # git status is dirty, create archive from stash
        os.system(
            f'git archive -o {args.path}/temporary_git_stash_archive.tar `git stash create` {git_root_directory}'
        )
    else:
        # git status is clean, create archive from HEAD
        os.system(
            f'git archive -o {args.path}/temporary_git_stash_archive.tar HEAD {git_root_directory}'
        )
    print(f'Unpacking git archive to {repository_copy_path}')
    os.system(f'tar -xf {args.path}/temporary_git_stash_archive.tar -C {repository_copy_path}')
    os.system(f'rm {args.path}/temporary_git_stash_archive.tar')

print(f'Switching to repository directory {repository_copy_path}')
os.chdir(repository_copy_path)
print(f'Now in {os.getcwd()}')

qsub_command = 'qsub '
qsub_command += '-cwd '
qsub_command += f'-N {args.job_name} '
qsub_command += f'-t {args.taskrange_begin}-{args.taskrange_end} '
qsub_command += f'-l h=\'{args.node}\' ' if args.node is not None else ''
qsub_command += f'{args.launch_script} '
qsub_command += '1 ' if array_job else '0 '
qsub_command += f'{args.path} '

print('Running the following qsub command now')
print(qsub_command)
os.system(qsub_command)
