from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    # Task("RZ011", "exp1", "shaping", forward_file=True).run()
    Task("RZ011", "exp1", "shaping", forward_file=False).test_test()
    # try:
    #     PiTest("exp1").flush()
    # finally:
    #     PiTest("exp1").end()


