import json
import sympy as sp
import numpy as np
import math
import glob
import os
import pickle

from pkg_resources import resource_string, resource_filename


def get_config(module, filename):
    return json.loads(resource_string(module, filename))


def get_path(module, filename):
    return resource_filename(module, filename)


def get_latest_filename(path, filetype):
    list_of_files = glob.glob(os.path.join(path, filetype))
    return max(list_of_files, key=os.path.getctime)


def save_dict_as_json(dict_to_save, path, filename):
    """
    saves a dictionary as a json file at indicated location
    filename needs to end with .json
    """
    file_path = os.path.join(path, filename)
    out_file = open(file_path, "w")
    json.dump(dict_to_save, out_file)


def save_dict_as_pickle(dict_to_save, path, filename):
    file_path = os.path.join(path, filename)
    with open(file_path, 'wb') as f:
        pickle.dump(dict_to_save, f)


def load_pickle_as_dict(path, filename):
    file_path = os.path.join(path, filename)
    with open(file_path, 'rb') as f:
        dict_loaded = pickle.load(f)
    return dict_loaded


# def calculate_reward(time_wait):
#     """
#     reward function
#     :return: reward size in ul
#     """
#     return 2 * time_wait * math.exp(-time_wait / 10)

def calculate_reward(time_wait):
    if 0 <= time_wait < 1:
        return 0
    elif 1 <= time_wait < 2:
        return 0.3
    elif 2 <= time_wait < 3:
        return 1.2
    elif 3 <= time_wait < 4:
        return 3.8
    elif 4 <= time_wait < 5:
        return 7.3
    elif 5 <= time_wait < 6:
        return 9.2
    elif 6 <= time_wait < 7:
        return 9.8
    elif 7 <= time_wait:
        return 10

