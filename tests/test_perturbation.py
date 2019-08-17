"""Perform perturbation tests for swap methods
"""
from copy import deepcopy
import numpy as np
import sys

sys.path.append('C:\\Users\\CJ\\Documents\\GitHub\\lmpy')

from lmpy import Matrix
from lmpy.randomize.curveball_pub import curve_ball, find_presences
from lmpy.randomize.swap import swap_randomize, trial_swap

FILLS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
ITERATIONS = 20
SIZES = [(10, 10), (100, 100), (1000, 1000)]

METHODS = [
    #('swap_5000', lambda x: swap_randomize(x, 5000)),
    #('swap_30000', lambda x: swap_randomize(x, 30000)),
    #('swap_50000', lambda x: swap_randomize(x, 50000)),
    #('swap_fill', lambda x: swap_randomize(x, int(x.sum()))),
    #('swap_fill_2', lambda x: swap_randomize(x, int(x.sum() / 2.0))),
    #('swap_fill_4', lambda x: swap_randomize(x, int(x.sum() / 4.0))),
    #('swap_size', lambda x: swap_randomize(x, int(x.size))),
    #('swap_size_2', lambda x: swap_randomize(x, int(x.size / 2.0))),
    ('swap_size_4', lambda x: swap_randomize(x, int(x.size / 4.0))),

    #('trial_swap_5000', lambda x: trial_swap(x, num_trials=5000)),
    #('trial_swap_30000', lambda x: trial_swap(x, num_trials=30000)),
    #('trial_swap_50000', lambda x: trial_swap(x, num_trials=50000)),
    #('trial_8sum', lambda x: trial_swap(x, num_trials=int(8 * x.sum()))),
    ('trial_2size/fill', lambda x: trial_swap(x, num_trials=int(2 * x.size / (x.sum() / x.size)))),
    #('trial_swap_fill', lambda x: trial_swap(x, num_trials=int(x.sum()))),
    #('trial_swap_fill_2', lambda x: trial_swap(x, num_trials=int(x.sum() / 2.0))),
    #('trial_swap_fill_4', lambda x: trial_swap(x, num_trials=int(x.sum() / 4.0))),
    #('trial_swap_size', lambda x: trial_swap(x, num_trials=int(x.size))),
    #('trial_swap_size_2', lambda x: trial_swap(x, num_trials=int(x.size / 2.0))),
    #('trial_swap_size_4', lambda x: trial_swap(x, num_trials=int(x.size / 4.0))),

    ('curveball', lambda x: curve_ball(x, find_presences(x)))
]

# ............................................................................
def measure_perturbation(o_mtx, r_mtx):
    """Measure perturbation between matrices
    """
    tot = int(np.sum(o_mtx))
    changed = tot - len(np.where(o_mtx + r_mtx == 2)[0])
    return 1.0 * changed / tot

# ............................................................................
if __name__ == '__main__':
    for r,c in SIZES:
        for fill in FILLS:
            num_ones = int(fill * r * c)
            tmp = np.zeros((r * c), dtype=np.int)
            tmp[:num_ones] = 1
            np.random.shuffle(tmp)
            pam = Matrix(tmp.reshape((r, c)))
            for func_name, func in METHODS:
                #print('func: {}'.format(func_name))
                ps = []
                for i in range(ITERATIONS):
                    ps.append(measure_perturbation(pam, func(deepcopy(pam))))
                print('{},{} - {} - {}: {}'.format(
                    r, c, fill, func_name, np.mean(ps)))
        print('')
