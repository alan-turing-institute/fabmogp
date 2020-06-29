import numpy as np
import matplotlib.pyplot as plt
import mogp_emulator
from earthquake import create_problem, run_simulation, compute_moment
import sys
from pprint import pprint
from os.path import join, dirname, exists
from os import walk, makedirs
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


def run_fdfault_simulation(mpi_exec, fdfault_exec, results_dir):

    input_points = np.load(join(results_dir, "input_points.npy"))

    if np.ndim(input_points) == 1:
        input_points = np.array([input_points])

    with open(join(results_dir, "ed.pickle"), 'rb') as input:
        ed = pickle.load(input)

    # Now we can actually run the simulations. First, we feed the input points
    # to create_problem to write the input files, call run_simulation to
    # actually simulate them, and compute_moment to load the data and compute
    # the earthquake size. The simulation is parallelized, so if you have
    # multiple cores available you can specify more processors to run the
    # simulation.
    counter = 1
    for point in input_points:
        name = "simulation_{}".format(counter)
        create_problem(point, name=name, output_dir=results_dir)
        run_simulation(name=name, n_proc=4, mpi_exec=mpi_exec,
                       fdfault_exec=fdfault_exec, output_dir=results_dir)
        counter += 1

    # save input_points array data into file
    np.save('input_points.npy', input_points)


def load_results(results_dir):

    ed = None
    input_points = []
    results = []
    # walk through all files in results_dir
    for r, d, f in walk(results_dir):
        # r=root, d=directories, f = files
        for file in f:
            if file == 'simulation_1.in':
                result = compute_moment(
                    name="simulation_1", results_dir=dirname(r))
                results.append(result)
            elif file == 'input_points.npy':
                input_points.append(np.load(join(r, file))[0])
            elif file == "ed.pickle" and ed is None:
                with open(join(r, file), 'rb') as input:
                    ed = pickle.load(input)

    input_points = np.array(input_points)
    results = np.array(results)

    return input_points, results, ed

def run_mogp_analysis(analysis_points, known_value, threshold, results_dir):

    input_points, results, ed = load_results(results_dir)

    # fit GP to simulations

    gp = mogp_emulator.GaussianProcess(input_points, results)
    gp.learn_hyperparameters()

    # We can now make predictions for a large number of input points much
    # more quickly than running the simulation.

    query_points = ed.sample(analysis_points)
    predictions = gp.predict(query_points)

    # set up history matching

    hm = mogp_emulator.HistoryMatching(obs=known_value, expectations=predictions,
                                       threshold=threshold)

    implaus = hm.get_implausibility()
    NROY = hm.get_NROY()

    # make some plots

    plt.figure()
    plt.plot(query_points[NROY, 0], query_points[NROY, 1], 'o')
    plt.xlabel('Normal Stress (MPa)')
    plt.ylabel('Shear to Normal Stress Ratio')
    plt.xlim((-120., -80.))
    plt.ylim((0.1, 0.4))
    plt.title("NROY Points")
    plt.savefig("results/nroy.png")

    import matplotlib.tri

    plt.figure()
    tri = matplotlib.tri.Triangulation(-(query_points[:,0]-80.)/40., (query_points[:,1]-0.1)/0.3)
    plt.tripcolor(query_points[:,0], query_points[:,1], tri.triangles, implaus,
                  vmin = 0., vmax = 6., cmap="viridis_r")
    cb = plt.colorbar()
    cb.set_label("Implausibility")
    plt.xlabel('Normal Stress (MPa)')
    plt.ylabel('Shear to Normal Stress Ratio')
    plt.title("Implausibility Metric")
    plt.savefig("results/implausibility.png")


if __name__ == "__main__":

    # Parse command line options
    mood = sys.argv[1]
    if mood == "run_simulation":
        mpi_exec = sys.argv[2]
        fdfault_exec = sys.argv[3]
        results_dir = sys.argv[4]

        try:
            sample_points = int(sys.argv[5])
        except ValueError:
            print("Error : input sample points should be integer value !")
            exit()

        run_fdfault_simulation(mpi_exec, fdfault_exec, results_dir)

    elif mood == "analysis":
        try:
            analysis_points = int(sys.argv[2])
        except ValueError:
            print("Error: number of analysis points must be an integer")
            exit()
        try:
            known_value = float(sys.argv[3])
        except ValueError:
            print("Error: known value must be a float")
            exit()
        try:
            threshold = float(sys.argv[4])
        except ValueError:
            print("Error: threshold must be a float")
            exit()
        results_dir = sys.argv[5]

        run_mogp_analysis(analysis_points, known_value, threshold, results_dir)
