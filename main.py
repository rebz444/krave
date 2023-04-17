from krave.experiment.task import Task
from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    Task("TEST", "exp1", "rig2", "regular", forward_file=False).run()

    # try:
    #     PiTest("exp1", "rig2").free_reward()
    # finally:
    #     PiTest("exp1", "rig2").end()


