from krave.experiment.session import Session
from krave.experiment.hardware_test import PiTest


def main(mouse, exp_name, hardware_config_name):
    info = {
        "mouse": mouse,
        "exp_name": exp_name,
        "hardware_config_name": hardware_config_name
    }
    session = Session(info)


if __name__ == '__main__':
    # PiTest("exp1").test_visual_with_lick(600, 300)
    PiTest("RZ002", "exp1").test_lick_with_mouse(5)
    # PiTest("RZ001", "exp1").test_water(0.03, 0.5)
    # main('RZ001', 'exp1')
    # PiTest("RZ001", "exp1").test_data_writer()


