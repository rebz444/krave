#!/bin/python3
from krave.experiment.task import Task
import sys

if os.path.exists(PATHS.COMMUNICATION):
    with open(PATHS.COMMUNICATION2, "r") as file:
        reader = csv.reader(file)
        reader[0] = rig_name_var
        reader[1] = training_var
        reader[2] = trainer_var
        reader[3] = record_var
        reader[4] = forward_file_var
        reader[5] = mouse_var
    os.remove(PATHS.COMMUNICATION)
else:
    print("Data Error")
    sys.exit(1)

#Testing
if __name__ == '__main__':
    Task(mouse=mouse_var,
         rig_name=rig_name_var,
         training=training_var,
         trainer=trainer_var,
         record=record_var,
         forward_file = forward_file_var).run()

#Original
'''
if __name__ == '__main__':
    Task(mouse="test",
         rig_name="rig1",
         training="regular",
         trainer="Rebekah",
         record=True).run()
'''

'''execute: 
$ chmod +x run_task.sh
in first instalation'''