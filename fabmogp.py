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
        env.sample_points = 5

    execute(put_configs, config)

    job(dict(script='mogp'), args)


@task
def mogp_analysis(results_dir):
    """
    run : fab localhost mogp_analysis:demo_localhost_16
    """
    # update_environment(args)
    # with_config(config)
    env.mood = "run_simulation"

    local("python3 %s/%s/run.py analysis %s  %s  %s/%s " %
          (env.local_results, results_dir,
           env.mpi_exec, env.fdfault_exec,
           env.local_results, results_dir))
