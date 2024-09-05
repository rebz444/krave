from krave.experiment.hardware_test import PiTest


if __name__ == '__main__':
    PiTest("rig7").free_reward(reward_size=2, num_rewards=50)
