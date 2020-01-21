# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to fabmogp.

from base.fab import *
from pprint import pprint

# Add local script, blackbox and template path.
add_local_paths("fabmogp")


@task
def mogp(config, **args):
    """
    Submit a single mogp job to the remote queue.
    The job results will be stored with a name pattern as defined in the environment,
    run : fab localhost mogp:demo
    """
    update_environment(args)
    with_config(config)
    env.mood = "run_simulation"
    if (hasattr(env, 'sample_points') == False):
        env.sample_points = 1

    local("python3 %s/init_config.py --sample_points %s --results_dir %s " %
          (env.job_config_path_local,
           env.sample_points,
           env.job_config_path_local)
          )
    execute(put_configs, config)

    job(dict(script='mogp'), args)


@task
def mogp_ensemble(config, sample_points=1, script='mogp', **args):
    """
    Submits an ensemble of mogp jobs.
    One job is run for each file in <config_file_directory>/SWEEP.
    run : fab localhost mogp_ensemble:demo,sample_points=5
    """
    update_environment(args)
    with_config(config)
    path_to_config = find_config_file_path(config)
    sweep_dir = path_to_config + "/SWEEP"
    env.script = script
    env.sample_points = sample_points
    env.mood = "run_simulation"

    # clean SWEEP directory
    local("rm -rf %s/*" % (sweep_dir))
    # generate a separated SWEEP folder for each sample_point
    for i in range(1, int(sample_points) + 1):
        folder_name = "sample_point_" + str(i)
        local("mkdir -p %s/%s" % (sweep_dir, folder_name))

    local("python3 %s/init_config.py --sample_points %s --results_dir %s --isSWEEP True" %
          (env.job_config_path_local,
           env.sample_points,
           env.job_config_path_local)
          )

    run_ensemble(config, sweep_dir, **args)


@task
def mogp_analysis(config, results_dir):
    """
    run : fab localhost mogp_analysis:demo,demo_localhost_16

    make sure that you already fetch the results:
                        fab localhost fetch_results
    """
    with_config(config)
    env.mood = "run_simulation"

    local("python3 %s/run.py analysis %s  %s  %s/%s " %
          (env.job_config_path_local,
           env.mpi_exec, env.fdfault_exec,
           env.local_results, results_dir))
