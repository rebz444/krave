# from krave.experiment.session import Session
from krave.experiment.hardware_test import PiTest
from krave.experiment.experiment_test import Task


def main(mouse, exp_name, hardware_config_name):
    pass


if __name__ == '__main__':
    # PiTest("RZ001", "exp1").test_visual_with_lick(600, 300)
    # PiTest("RZ001", "exp1").test_task()
    # PiTest("RZ001", "exp1").reset()
    # PiTest("RZ001", "exp1").test_visual_cue(600, 300)
    # PiTest("RZ001", "exp1").test_water(run_time=20, open_time=0.01, cool_time=0.8)
    # PiTest("RZ002", "exp1").lick_validation(n_licks=10, time_limit=30)
    # Task("RZ001", "exp1").session()
    Task("RZ001", "exp1").shaping(2)
    # Task("RZ001", "exp1").test_reward_optimal()
    # PiTest("RZ001", "exp1").reset()





