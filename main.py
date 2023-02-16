from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    try:
        # PiTest("exp1").flush()
        Task("RZ011", "exp1", "shaping2", forward_file=False).test_test()
    finally:
        PiTest("exp1").end()


