import sys
import os
import argparse
import shutil

#import python_entry

parser = argparse.ArgumentParser()
parser.add_argument('--launch_script',
                    type=str)
parser.add_argument('--path',
                    type=str,
                    help='destination of results')
parser.add_argument('--params_path',
                    type=str,
                    default='src/parameters.yaml',
                    help='path to parameters YAML file')
parser.add_argument('--taskrange_begin',
                    type=int,
                    default=1)
parser.add_argument('--taskrange_end',
                    type=int,
                    default=1)
parser.add_argument('--job_name',
                    type=str)
args = parser.parse_args()
output_path = os.path.abspath(args.path)

if os.path.exists(output_path):
    print(f"Output directory {output_path} already exists, "
          "should we continue?")
    if not input('[y to continue]') == 'y':
        sys.exit('Ok, no job started')

if not os.path.exists(output_path):
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path, 'stdin_and_out'))


gridsearch = True if args.taskrange_end - args.taskrange_begin > 0 else False
if not gridsearch:
    shutil.copyfile(args.params_path, os.path.join(output_path, 'parameters.yaml'))
#####
##### python_entry stuff
#####

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
        os.systme(f'git archive HEAD -o {output_path}/temporary_git_stash_archive.tar')
    print(f'Unpacking git archive to {repository_copy_path}')
    os.system(f'tar -xf {output_path}/temporary_git_stash_archive.tar -C {repository_copy_path}')
    os.system(f'rm {output_path}/temporary_git_stash_archive.tar')

print(f'Switching to repository directory {repository_copy_path}')
os.chdir(repository_copy_path)
print(f'Now in {os.getcwd()}')

os.environ['OUTPUT_PATH'] = output_path
qsub_command = (
    f'export OUTPUT_PATH="{output_path}" && ' +
    'qsub ' +
    '-cwd ' +
    f'-N {args.job_name} ' +
    f'-t {args.taskrange_begin}-{args.taskrange_end} ' +
    f'{args.launch_script} ' +
    f'{output_path}'
)
print('Running the following qsub command now')
print(qsub_command)
os.system(qsub_command)
