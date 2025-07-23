#!/bin/python3
from krave.experiment.task import Task
from krave.ui.constants import PATHS
import sys
import os
import csv
import time

def get_experiment_options_data():
    '''Read data from communication_to_ui.txt written by UI.py and provided by the tkinter selection of conditions script'''
    
    options = []

    timeout = 10  # seconds
    start = time.time()
    while not os.path.exists(PATHS.COMMUNICATION_TO_UI):
        if time.time() - start > timeout:
            print("Data Error: Params file not found after waiting.")
            sys.exit(1)
        time.sleep(0.2)
    with open(PATHS.COMMUNICATION_TO_UI, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            options.append(row)
    os.remove(PATHS.COMMUNICATION_TO_UI)

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

    return(options)


if __name__ == '__main__':
    options = get_experiment_options_data()

    Task(mouse=options[5],
         rig_name=options[0],
         training=options[1],
         trainer=options[2],
         record=options[3],
         forward_file = options[4]).run()


'''execute: 
$ chmod +x run_task.sh
in first instalation'''