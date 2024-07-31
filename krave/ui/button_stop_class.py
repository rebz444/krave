from krave.ui.button_class import Button
from krave.ui.constants import PATHS


class StopButton(Button):
    def activate(self):
        self.activated = True
        return False

