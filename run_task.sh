#!/bin/python3
from krave.experiment.task import Task
from krave.ui.constants import PATHS
import sys
import os
import csv

def get_experiment_options_data():
    '''Read data from communications2 written by UI.py and provided by the tkinter selection of conditions script'''
    
    options = []

    if os.path.exists(PATHS.COMMUNICATION2):
        with open(PATHS.COMMUNICATION2, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                options.append(row)
        os.remove(PATHS.COMMUNICATION2)
    else:
        print("Data Error")
        sys.exit(1)

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