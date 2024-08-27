from krave.ui.button_class import Button
from krave.ui.constants import PATHS
import subprocess
import time
import os

class StartButton(Button):
    def activate(self):
        '''This function is triggered when the button is pressed. 
        It starts the .sh file and reads the data path where the data is being written
        After it removes the communication file'''
        self.activated = True
        self.RUN_TASK = subprocess.Popen(["/bin/python3", PATHS.RUN_TASK])
        print(self.RUN_TASK.stdout)

        time.sleep(25)

        with open(PATHS.COMMUNICATION, "r") as file:
            self._source_data_path = file.read()

        if os.path.exists(PATHS.COMMUNICATION):
            os.remove(PATHS.COMMUNICATION)
        else:
            print("File doesn't exists")

        return self._source_data_path

