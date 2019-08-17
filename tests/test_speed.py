"""Perform perturbation tests for swap methods
"""
from copy import deepcopy
import numpy as np
import sys
import time

from lmpy import Matrix
from lmpy.randomize.curveball_pub import curve_ball, find_presences
from lmpy.randomize.grady import (
    grady_randomize, all_ones_heuristic, all_zeros_heuristic, 
    fill_shuffle_reshape_heuristic, max_col_or_row_heuristic, 
    min_col_or_row_heuristic, total_fill_percentage_heuristic)
from lmpy.randomize.swap import swap_randomize, trial_swap

DEADLINE_TIME = 600
FILLS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
ITERATIONS = 10
SIZES = [(10, 10), (100, 100), (1000, 1000), (10000, 10000), (100000, 10000)]

METHODS = [
    ('grady_all_ones', lambda x: grady_randomize(
        x, approximation_heuristic=all_ones_heuristic)),
    ('grady_all_zeros', lambda x: grady_randomize(
        x, approximation_heuristic=all_zeros_heuristic)),
    ('grady_fill_shuffle', lambda x: grady_randomize(
        x, approximation_heuristic=fill_shuffle_reshape_heuristic)),
    ('grady_max_col_row', lambda x: grady_randomize(
        x, approximation_heuristic=max_col_or_row_heuristic)),
    ('grady_min_col_row', lambda x: grady_randomize(
        x, approximation_heuristic=min_col_or_row_heuristic)),
    ('grady_total_fill', lambda x: grady_randomize(
        x, approximation_heuristic=total_fill_percentage_heuristic)),

    #('swap_5000', lambda x: swap_randomize(x, 5000)),
    #('swap_30000', lambda x: swap_randomize(x, 30000)),
    #('swap_50000', lambda x: swap_randomize(x, 50000)),
    #('swap_fill', lambda x: swap_randomize(x, int(x.sum()))),
    #('swap_fill_2', lambda x: swap_randomize(x, int(x.sum() / 2.0))),
    ('swap_fill_4', lambda x: swap_randomize(x, int(x.sum() / 4.0))),
    #('swap_size', lambda x: swap_randomize(x, int(x.size))),
    #('swap_size_2', lambda x: swap_randomize(x, int(x.size / 2.0))),
    #('swap_size_4', lambda x: swap_randomize(x, int(x.size / 4.0))),

    #('trial_swap_5000', lambda x: trial_swap(x, num_trials=5000)),
    #('trial_swap_30000', lambda x: trial_swap(x, num_trials=30000)),
    #('trial_swap_50000', lambda x: trial_swap(x, num_trials=50000)),
    #('trial_swap_fill', lambda x: trial_swap(x, num_trials=int(x.sum()))),
    #('trial_swap_fill_2', lambda x: trial_swap(x, num_trials=int(x.sum() / 2.0))),
    #('trial_swap_fill_4', lambda x: trial_swap(x, num_trials=int(x.sum() / 4.0))),
    #('trial_swap_size', lambda x: trial_swap(x, num_trials=int(x.size))),
    #('trial_swap_size_2', lambda x: trial_swap(x, num_trials=int(x.size / 2.0))),
    #('trial_swap_size_4', lambda x: trial_swap(x, num_trials=int(x.size / 4.0))),
    ('trial_2size/fill', lambda x: trial_swap(x, num_trials=int(2 * x.size / (x.sum() / x.size)))),

    ('curveball', lambda x: curve_ball(x, find_presences(x)))
]

# ............................................................................
if __name__ == '__main__':
    size_methods = METHODS
    for r,c in SIZES:
        print('Size: {}, {}'.format(r, c))
        times = {}
        for f_name, _ in size_methods:
            times[f_name] = {}
            for fill in FILLS:
                times[f_name][fill] = []
        for fill in FILLS:
            print('  - fill {}'.format(fill))
            num_ones = int(fill * r * c)
            tmp = np.zeros((r * c), dtype=np.int)
            tmp[:num_ones] = 1
            np.random.shuffle(tmp)
            pam = Matrix(tmp.reshape((r, c)))
            for func_name, func in METHODS:
                for i in range(ITERATIONS):
                    a_time = time.time()
                    _ = func(deepcopy(pam))
                    b_time = time.time()
                    times[func_name][fill].append(b_time - a_time
        new_ms = []
        for f_name, fn in size_methods:
            avg_times = [np.mean(times[f_name][fill]) for fill in FILLS]
            test_time = np.mean(avg_times)
            # Write out all results
            print('{}, avg: {}, times: {}'.format(f_name, test_time, avg_times))
            if test_time < DEADLINE_TIME:
                new_ms.append((f_name, fn))
            else:
                print('Dropping out {}'.format(f_name))
        size_methods = new_ms
