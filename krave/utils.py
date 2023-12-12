import json

from pkg_resources import resource_string, resource_filename


def get_config(module, filename):
    return json.loads(resource_string(module, filename))


def get_path(module, filename):
    return resource_filename(module, filename)


def get_exp_name(mouse):
    cohort = get_config('krave', f'config/cohort.json')
    for exp_name, mice in cohort.items():
        if mouse in mice:
            print(exp_name)
            return exp_name
        else:
            raise Exception('Invalid mouse name')

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


if __name__ == '__main__':
    get_exp_name('RZ099')
