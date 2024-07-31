#!/bin/python3
from krave.experiment.task import Task    

#Testing
if __name__ == '__main__':
    Task(mouse="test",
         rig_name="rig2",
         training="regular",
         trainer="Rebekah",
         record=True,
         forward_file = False).run()

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