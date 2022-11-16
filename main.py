from krave.experiment.hardware_test import PiTest
from krave.experiment.experiment_test import Task


def main(mouse, exp_name, hardware_config_name):
    pass


if __name__ == '__main__':
    # PiTest("RZ001", "exp1").test_visual_with_lick(600, 300)
    # PiTest("RZ001", "exp1").test_visual_cue(600, 300)
    # PiTest("RZ001", "exp1").test_water(iterations=50, open_time=0.02, cool_time=0.2)
    # PiTest("RZ002", "exp1").lick_validation(n_licks=10, time_limit=30)
    # Task("RZ001", "exp1").session()
    Task("RZ007", "exp1").shaping(1)
    # PiTest("RZ001", "exp1").spout_calibration()
    # PiTest("RZ001", "exp1").reset()





