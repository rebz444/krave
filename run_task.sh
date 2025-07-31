#!/bin/python3
from krave.experiment.task import Task
from krave.ui.constants import PATHS
import sys
import os
import csv
import time

def get_experiment_options_data():
    '''Read data from communication_from_ui.txt written by UI.py and provided by the tkinter selection of conditions script'''
    
    options = []

    timeout = 10  # seconds
    start = time.time()
    while not os.path.exists(PATHS.COMMUNICATION_FROM_UI):
        if time.time() - start > timeout:
            print("Data Error: Params file not found after waiting.")
            sys.exit(1)
        time.sleep(0.2)
    with open(PATHS.COMMUNICATION_FROM_UI, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            options.append(row)
    os.remove(PATHS.COMMUNICATION_FROM_UI)

    for i in range(len(options)):
        options[i] = options[i][0]

    if options[3] == "True":
        options[3] = True
    else:
        options[3] = False

    if options[4] == "True":
        options[4] = True
    else:
        options[4] = False

    # Parse override parameters
    max_reward_override = None
    max_time_override = None
    max_missed_trial_override = None
    
    if len(options) >= 7 and options[6].strip():  # max_reward_override
        try:
            max_reward_override = float(options[6]) if '.' in options[6] else int(options[6])
        except ValueError:
            print(f"Warning: Invalid max_reward_override value: {options[6]}")
    
    if len(options) >= 8 and options[7].strip():  # max_time_override
        try:
            max_time_override = float(options[7]) if '.' in options[7] else int(options[7])
        except ValueError:
            print(f"Warning: Invalid max_time_override value: {options[7]}")
    
    if len(options) >= 9 and options[8].strip():  # max_missed_trial_override
        try:
            max_missed_trial_override = int(options[8])
        except ValueError:
            print(f"Warning: Invalid max_missed_trial_override value: {options[8]}")
    
    # Add override parameters to options
    options.extend([max_reward_override, max_time_override, max_missed_trial_override])

    return(options)


if __name__ == '__main__':
    options = get_experiment_options_data()

    Task(mouse=options[5],
         rig_name=options[0],
         training=options[1],
         trainer=options[2],
         record=options[3],
         forward_file=options[4],
         max_reward_override=options[9],
         max_time_override=options[10],
         max_missed_trial_override=options[11]).run()


'''execute: 
$ chmod +x run_task.sh
in first instalation'''