from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest
from krave import utils


if __name__ == '__main__':
    try:
        PiTest("exp1").spout_calibration()
    finally:
        PiTest("exp1").end()


