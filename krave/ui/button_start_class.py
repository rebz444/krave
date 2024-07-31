from krave.ui.button_class import Button
from krave.ui.constants import PATHS
import subprocess
import time
import os

class StartButton(Button):
    def activate(self):
        self.activated = True
        self.RUN_TASK = subprocess.Popen(["/bin/python3", PATHS.RUN_TASK])
        print(self.RUN_TASK.stdout)

        time.sleep(5)

        with open(PATHS.INITIAL_COMMUNICATION, "r") as file:
            self._source_data_path = file.read()

        if os.path.exists(PATHS.INITIAL_COMMUNICATION):
            os.remove(PATHS.INITIAL_COMMUNICATION)
        else:
            print("File doesn't exists")

        return self._source_data_path

