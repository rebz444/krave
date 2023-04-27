from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    try:
        # PiTest("exp1", "rig3").pump_calibrate()
        PiTest("exp1", "rig3").test_lick_sensor()
    finally:
        PiTest("exp1", "rig3").end()
