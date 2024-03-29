from os.path import join
import fdfault
import fdfault.analysis
import numpy as np
from utils import generate_profile, generate_normals_2d, rotate_xy2nt_2d
import subprocess
from scipy.integrate import simps


def create_problem(arg, name="rough_example",
                   outname="ufault",
                   refine=1,
                   output_dir="", vy_snapshot=False):
    """
    Create demo problem

    Inputs:
    Required:
    arg = 1d array of length 3 holding simulation inputs
          (shear/normal stress, normal stress,
          ratio of out of plane to in plane normal component)
    Optional:
    name = problem name (string)
    outname = name of output file (string)
    refine = simulation refinement(default is 1, which should be fine for this)

    Outputs:
    None

    Note: function will fail if the stress on any point of the fault exceeds
    the strength. Should (probably) not occur for the parameter range specified
    in the demo, but in here for safety purposes.
    """

    assert len(arg) == 3

    syy, ston, sxtosy = arg

    p = fdfault.problem(name)

    # set rk and fd order

    p.set_rkorder(4)
    p.set_sbporder(4)

    # set problem info

    nt = 800 * refine + 1
    nx = 400 * refine + 1
    ny = 150 * refine + 1
    lx = 32.
    ly = 12.

    p.set_nt(nt)
    p.set_cfl(0.3)
    p.set_ninfo((nt - 1) // 4)

    # set number of blocks and coordinate information

    p.set_nblocks((1, 2, 1))
    p.set_nx_block(([nx], [ny, ny], [1]))

    # set block dimensions

    p.set_block_lx((0, 0, 0), (lx, ly))
    p.set_block_lx((0, 1, 0), (lx, ly))

    # set block boundary conditions

    p.set_bounds((0, 0, 0), ['absorbing', 'absorbing', 'absorbing', 'none'])
    p.set_bounds((0, 1, 0), ['absorbing', 'absorbing', 'none', 'absorbing'])

    # set block surface

    sxx = sxtosy * syy
    sxy = -syy * ston

    x = np.linspace(0., lx, nx)
    y = ly * np.ones(nx) + generate_profile(nx, lx, 1.e-2, 20, 1., 18749)

    surf = fdfault.curve(nx, 'y', x, y)

    # set initial fields

    norm_x, norm_y = generate_normals_2d(x, y, 'y')
    sn = np.zeros(nx)
    st = np.zeros(nx)

    for i in range(nx):
        sn[i], st[i] = rotate_xy2nt_2d(
            sxx, sxy, syy, (norm_x[i], norm_y[i]), 'y')

    assert np.all(st + 0.7 * sn < 0.), "shear stress is too high"

    p.set_block_surf((0, 0, 0), 3, surf)
    p.set_block_surf((0, 1, 0), 2, surf)

    p.set_stress((sxx, sxy, 0., syy, 0., 0.))

    # set interface type

    p.set_iftype(0, 'slipweak')

    # set slip weakening parameters

    p.add_pert(fdfault.swparam('constant', dc=0.8, mus=0.7, mud=0.2), 0)
    p.add_pert(fdfault.swparam('boxcar', x0=2., dx=2., mus=10000.), 0)
    p.add_pert(fdfault.swparam('boxcar', x0=30., dx=2., mus=10000.), 0)

    # add load perturbation

    nuc_pert = np.zeros((nx, 1))
    idx = (np.abs(x - lx / 2.) < 2.)
    nuc_pert[idx, 0] = (-0.7 * sn[idx] - st[idx]) + 0.1

    p.set_loadfile(0, fdfault.loadfile(
        nx, 1, np.zeros((nx, 1)), nuc_pert, np.zeros((nx, 1))))

    # add output unit
    p.set_datadir(join(output_dir, "data"))
    if vy_snapshot:
        p.add_output(fdfault.output("vybody", "vy", (nt - 1)*3//4, (nt - 1)*3//4, 1,
                                    0, nx - 1, 1, 0, 2*ny - 1, 1, 0, 0, 1))
    p.add_output(fdfault.output(outname, 'U', nt, nt, 1,
                                0, nx - 1, 1, ny, ny, 1, 0, 0, 1))

    p.write_input(directory=join(output_dir, "problems"))


def run_simulation(name="rough_example",
                   n_proc=1,
                   mpi_exec=None,
                   fdfault_exec=None,
                   output_dir=""):
    """
    launches problem with specified number of processes
    """
    subprocess.run([mpi_exec, "-n", str(int(n_proc)),
                join(fdfault_exec, "fdfault"), output_dir + "/problems/" + name + ".in"],
               cwd=fdfault_exec)


def compute_moment(name="rough_example",
                   outname="ufault",
                   results_dir=None):
    """
    computes seismic moment for a given problem
    """

    datadir = join(results_dir, "data")
    U = fdfault.analysis.output(name, outname, datadir)
    U.load()

    return simps(U.U, U.x)
