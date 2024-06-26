# Gridsearch Helper
This repository contains some helper scripts to launch your parallelized gridsearch with the SLURM scheduling system. Additionally it also provides a python package to collect and visualize the results of the gridsearch, but that is currently unmaintained.

## What problems does `gridsearch_helper` solve?
A common problem is that you want to run a grid search over hyperparameters. For simple grid searches, this is not very complicated, but for more complex setups (e.g. including nested hyperparameter dicts), this becomes cumbersome. `gridsearch_helper` helps with that. Additionally, sometimes you want to run several gridsearches simultaneously and change the code in between. A problem occurs if you start a gridsearch and some jobs are put into the waiting queue. Then you change the code for another gridsearch that you want to run. The jobs from your old gridsearch will eventually get activated, but they will now run the new code, which you are in the middle of changing! `gridsearch_helper` helps with that, too. Every time you start a new job, a copy of the current version of your repository is made. The gridsearch is then executed within this copy. What's especially great about this is that this happens without you even noticing or having to care about it.

## Requirements in your code
In order for this to work, unfortunately some assumptions have to be made about your code. I hope that making modifications to your code such that it fulfills these requirements is not too hard.
- Your project must be version controlled with git
- Your code must be able to read its hyperparameters from a `YAML` file, and your code must accept a command line parameter `--parameters_file=...` which tells it from where to read the `YAML` file.
- if you use data or other external files in your code, either these data need to be part of your git repository, or your code must use absolute paths to these data
- Your code must be set up such that it takes a command line parameter `--path=...` and writes all its output in (subfolders of) this path

## Installation and Usage - running gridsearch jobs
First, make sure the follwing dependencies are installed:

- PyYAML
- click

Place this repository anywhere on your system.

You need to have a `YAML` file containing the default parameters, and one key `'gridsearch'`, which contains lists of values for each parameter to gridsearch over. In case you have your parameters nested, that isn't a problem, for the purpose of the gridsearch we assign parameters as if the nesting was flattened.
```YAML
x_y_step: 0.1
zstep: -0.035
nn_architecture: ['dense50', 'softplus', 'dense100', 'softplus']
gamma: 0.9
target_update_rate: 1000
lr: 0.0003
initial_temperature: 3.001
learning_rule: double_q_learning
gridsearch:
  learning_rule:
  - double_q_learning
  - PPO
  target_update_rate:
  - 500
  - 1000
  - 10000
```
Then, from the working directory in which you want your program to be run, call the `slurmlaunch` script like this

```bash
path/to/gridsearch_helper/SLURM/slurmlaunch --taskrange-begin=1 --taskrange-end=5 --time=00:10:00 --partition=cpu-2h --params-path=parameters.yaml --path=outfiles/test
```
The results will be put in ``./outfiles/test``, which is a path relative to your current working directory.

## Usage - analyzing results
This repository also contains a package ``gridsearch_analysis``. ``gridsearch_analysis`` can be installed by simply running ``pip install .`` from the root of this repository.
``gridsearch_analysis`` assumes that the above instructions were followed. Continuing with the above example, there is a folder `outfiles/test`, and it has subfolders `outfiles/test/00001`, `outfiles/test/00002` etc. Each subfolder contains a file `parameters.yaml`, which is generated by `slurmlaunch` and contains the parameters as assigned by `slurmlaunch`. Additionally, `slurmlaunch` creates another file called `run_info.yaml` which contains things like the run time, git status etc. If your code writes a file `results.yaml` into that folder, that would be great. You can then use the function ``collect_results()``, which loops over all subfolders and collects all values in ``parameters.yaml``, ``run_info.yaml`` and ``results.yaml`` into a pandas dataframe.

```python
from gridsearch_analysis import collect_results

results_path = os.path.join('outfiles', 'test')
df = collect_results.collect_results(results_path)
```

Furthermore, ``gridsearch_analysis`` can also make plots of the collected results. It will plot the performance as measured by some variable ``target_column`` as a function of user-specified indpendent variables ``relevant_parameters``. The type of plot created depends on how many independent variables you specify. If you have:
- 0  independent variables: create a swarm/barplot with a single group that contains all runs
- 1  independent variable: create a swarm/barplot with one group for each value of the independent variable
- 2+ independent variables: create a parallel coordinates plot

There is also an option to split the analysis into separate parts via the values of another independent variable. In this case, one plot per value of this ``split_analysis_column`` is performed.

See the file `gridsearch_analysis/run.py` for an example how to use `gridsearch_analysis`.
