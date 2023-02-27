from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    # Task("RZ011", "exp1", "regular", forward_file=True).run()
    #
    try:
        PiTest("exp1").test_syringe_pump()
    finally:
        PiTest("exp1").end()


