import json

from pkg_resources import resource_string, resource_filename


def get_config(module, filename):
    return json.loads(resource_string(module, filename))


def get_path(module, filename):
    return resource_filename(module, filename)


def get_exp_name(mouse):
    cohort = get_config('krave', 'config/cohort.json')
    exp_name = None  # Initialize exp_name as None

    for exp, mice in cohort.items():
        if mouse in mice:
            exp_name = exp
        elif mouse.lower() == 'test':
            exp_name = input("Enter the experiment name: ")
            break

    if exp_name is None:
        raise Exception('Invalid mouse name')

    print(exp_name)
    return exp_name


if __name__ == '__main__':
    get_exp_name('test')
