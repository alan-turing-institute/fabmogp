import numpy as np
import mogp_emulator
from optparse import OptionParser
from pprint import pprint
from os.path import join

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


def mogp_configuration_initialization(sample_points,
                                      results_dir,
                                      isSWEEP, seed=0):

    ed = mogp_emulator.LatinHypercubeDesign(
        [(-120., -80.), (0.1, 0.4), (0.9, 1.1)])

    # We can now generate a design of sample_points by calling the sample

    if seed == 0:
        seed = None

    np.random.seed(seed)
    input_points = ed.sample(sample_points)

    if isSWEEP == False:
        # save input_points array data into file
        np.save(join(results_dir, "input_points.npy"), input_points)
        with open(join(results_dir, "ed.pickle"), 'wb') as output:
            pickle.dump(ed, output, pickle.HIGHEST_PROTOCOL)
    else:
        counter = 1
        for point in input_points:
            folder_name = "sample_point_" + str(counter)
            np.save(join(results_dir, "SWEEP", folder_name,
                         "input_points.npy"), point)
            counter += 1
            with open(join(results_dir, "SWEEP", folder_name, "ed.pickle"),
                      'wb') as output:
                pickle.dump(ed, output, pickle.HIGHEST_PROTOCOL)
