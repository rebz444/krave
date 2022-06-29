from krave.experiment.session import Session
from krave.experiment.hardware_test import PiTest


def main(mouse, exp_name, hardware_config_name):
    pass


if __name__ == '__main__':
    # PiTest("exp1").test_visual_with_lick(600, 300)
    # PiTest("RZ001", "exp1").test_water(0.03, 0.5)
    PiTest("RZ001", "exp1").test_lick_with_mouse(15, 30)
    # PiTest("RZ002", "exp1").test_camera()
    # PiTest("RZ001", "exp1").test_data_writer()


