from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    # Task("TEST", "exp1", "regular", forward_file=False).run()

    PiTest("exp1", "rig2").test_pulse()
    # try:
        # PiTest("exp1").calibrate_pump_pin_1()
        # PiTest("exp1", "rig2").test_pump()
    # finally:
    #     PiTest("exp1").end()


