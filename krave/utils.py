import json
import sympy as sp
import math

from pkg_resources import resource_string, resource_filename


def get_config(module, filename):
    return json.loads(resource_string(module, filename))


def get_path(module, filename):
    return resource_filename(module, filename)


def calculate_reward(time_wait):
    """
    reward function
    :return: reward size in ul
    """
    return 2 * time_wait * math.exp(-time_wait / 10)


def calculate_time_wait_optimal(time_bg):
    """
    :param time_bg: bg time length
    :return: optimal wait time per trial
    """
    t = sp.Symbol('t', real=True)
    r = 2 * t * sp.exp(-t / 10) / (t + time_bg)
    r_prime = r.diff(t)
    time_wait = sp.solve(r_prime, t)
    for i in time_wait:
        if i > 0:
            return round(i, 2)
