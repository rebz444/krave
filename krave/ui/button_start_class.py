from krave.ui.button_class import Button
from krave.ui.constants import PATHS
import subprocess
import time
import os

class StartButton(Button):
    def activate(self):
        '''This function is triggered when the button is pressed. 
        It now only sets activated to True and does not launch the experiment process.'''
        self.activated = True
        return None

