import time
import numpy as np


def test_runtime(first_function, second_function, init=None, between=None, n_runs=15):
    if init is not None:
        init()

    times = []

    for i in range(n_runs):
        start = time.clock()
        first_function()
        end = time.clock()
        times.append(end-start)

    f = np.mean(times)
    print("First:", f)

    if between is not None:
        between()

    for i in range(n_runs):
        start = time.clock()
        second_function()
        end = time.clock()
        times.append(end - start)

    s =  np.mean(times)
    print("Second:",s)

    if f > s:
        print("Second was faster by", f-s)
    else:
        print("First was faster by", s-f)