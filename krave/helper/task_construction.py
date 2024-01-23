import random
import numpy as np

from krave.helper import utils


class TaskConstruction:
    def __init__(self, exp_config):
        self.total_blocks = exp_config['total_blocks']  # total number of blocks per session
        self.total_trials_median = exp_config['total_trials_median']  # median number of trials per session
        self.block_length_range = exp_config['block_length_range']
        self.time_bg_lengths = exp_config['time_bg_lengths']
        self.time_bg_range = exp_config['time_bg_range']
        self.max_time_wait = exp_config['max_time_wait']

    def get_session_structure(self):
        """
        Determines the session structure based on the number of blocks and avg bg time for each block
        makes session_dict with block num as key and a list of background time for each trial as values
        time_bg_drawn from a uniform distribution with average of time_bg
        """
        # determine the length of each block
        trials_per_block = self.total_trials_median // self.total_blocks
        trials_per_block_min = trials_per_block - (self.block_length_range / 2)
        trials_per_block_max = trials_per_block + (self.block_length_range / 2)
        block_lengths = [random.randint(trials_per_block_min, trials_per_block_max) for _ in range(self.total_blocks)]
        total_trial_num = sum(block_lengths)

        # make block types alternate
        random.shuffle(self.time_bg_lengths)
        iterations = self.total_blocks // len(self.time_bg_lengths)
        block_list = self.time_bg_lengths * iterations

        session_dict = dict.fromkeys(range(self.total_blocks))
        for i, (l, t) in enumerate(zip(block_lengths, block_list)):
            low = t - t * self.time_bg_range
            high = t + t * self.time_bg_range
            drawn_times = np.random.uniform(low, high, l).tolist()
            drawn_times = [round(item, 1) for item in drawn_times]
            session_dict[i] = drawn_times

        if sum(len(times) for times in session_dict.values()) != total_trial_num:
            raise Exception('Missing time_bg!')
        print(f'length of each block: {block_lengths}')
        print(f'bg time of each block: {block_list}')
        print(f'{total_trial_num} trials total')
        return total_trial_num, session_dict

    def get_random_reward_time(self, session_dict):
        """
        used to deliver reward at random time post cue onset when reward delivery is not lick triggered
        makes a dictionary with block num as key and a list of random wait time for each trial as values
        randomly draws wait time
        """
        random_wait_dict = dict.fromkeys(range(self.total_blocks))
        for blk in session_dict:
            num_to_draw = len(session_dict[blk])
            drawn_times = np.random.uniform(0.5, self.max_time_wait, num_to_draw).tolist()
            random_wait_dict[blk] = [round(item, 1) for item in drawn_times]
        return random_wait_dict


if __name__ == '__main__':
    exp_config = utils.get_config('krave', 'config/exp1_long.json')
    TaskConstruction(exp_config).get_session_structure()
