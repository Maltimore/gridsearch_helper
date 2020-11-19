import os
import time


nodes = [
    'node01',
    'node02',
    'node03',
    'node04',
    'node05',
    'node06',
    'node07',
    'node08',
    'node09',
    'node10',
    'node11',
    'node12',
    'node13',
    'node15',
    'node16',
    'node18',
    'node19',
    'node20',
    'node21',
    'node22',
    'node23',
    'node24',
    'node26',
    'node27',
    'node28',
    'node29',
    'node30',
    'node31',
    'node32',
    'node33',
    'node34',
    'node35',
    'node36',
    'node37',
    'node41',
]

job_name = 'nodes1'
for node in nodes:
    command = (
        "/usr/bin/env launch_SGE_job.py" + " " +
        "--launch_script cluster/SGE_entry.sh" + " " +
        "--path " + os.path.join('outfiles', job_name, node) + " " +
        "--job_name " + job_name + " " +
        "--node " + node
    )
    print(f'\ncommand: {command}')
    os.system(command)
    # sleep a bit such that git can clean up its index.lock file
    time.sleep(5)
