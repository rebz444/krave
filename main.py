from krave.experiment.session import Session
from krave.experiment.hardware_test import PiTest

if __name__ == '__main__':
    PiTest("exp1").test_visual_cue(600, 300)


