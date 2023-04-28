import random
import numpy as np
import os

from krave import utils


class TaskConstruction:
    def __init__(self, exp_name, exp_config):
        self.exp_name = exp_name
        self.total_blocks = exp_config['total_blocks']  # total number of blocks per session
        self.total_trials_median = exp_config['total_trials_median']  # median number of trials per session
        self.block_length_range = exp_config['block_length_range']
        self.blocks = exp_config['blocks']

        # trial structure variables
        self.time_bg_range = exp_config['time_bg_range']
        self.max_wait_time = exp_config['max_wait_time']

    def get_session_structure(self):
        """
        Determines the session structure based on the number of blocks and avg bg time for each block
        makes session_dict with block num as key and a list of background time for each trial as values
        time_bg_drawn from a uniform distribution with average of time_bg
        """
        trials_per_block = self.total_trials_median // self.total_blocks
        trials_per_block_min = trials_per_block - (self.block_length_range / 2)
        trials_per_block_max = trials_per_block + (self.block_length_range / 2)
        block_lengths = []

        # make two block types alternate
        for i in range(self.total_blocks):
            block_lengths.append(random.randint(trials_per_block_min, trials_per_block_max))
        total_trial_num = sum(block_lengths)
        block_list = []
        block_types = list(self.blocks.values())
        first_block = random.choice(block_types)
        if first_block == block_types[0]:
            for i in range(self.total_blocks):
                if i % 2 == 0:
                    block_list.append(first_block)
                else:
                    block_list.append(block_types[1])
        elif first_block == block_types[1]:
            for i in range(self.total_blocks):
                if i % 2 == 0:
                    block_list.append(first_block)
                else:
                    block_list.append(block_types[0])

        count = 0
        session_dict = dict.fromkeys(range(self.total_blocks))
        for i, (l, t) in enumerate(zip(block_lengths, block_list)):
            low = t - t * self.time_bg_range
            high = t + t * self.time_bg_range
            drawn_times = np.random.uniform(low, high, l).tolist()
            drawn_times = [round(item, 1) for item in drawn_times]
            session_dict[i] = drawn_times
            count += len(drawn_times)

        if count != total_trial_num:
            raise Exception('Missing time_bg!')

        print(f'length of each block: {block_lengths}')
        print(f'bg time of each block: {block_list}')
        print(f'{total_trial_num} trials total')
        return total_trial_num, session_dict

    def get_wait_time_optimal(self, session_dict):
        """
        used to deliver reward at optimal wait time when reward delivery is not lick triggerd
        makes a dictionary with block num as key and a list of optimal wait time for each trial as values
        pulls optimal wait time from saved pickle
        """
        path = os.path.join('/home', 'pi', 'Documents', 'behavior_code', 'krave', 'experiment', 'config')
        filename = self.exp_name + '_optimal_value_dict.pkl'
        optimal_value_dict = utils.load_pickle_as_dict(path, filename)
        optimal_wait_dict = dict.fromkeys(range(self.total_blocks))
        for blk in session_dict:
            optimal_list = []
            for trl in session_dict[blk]:
                optimal_list.append(optimal_value_dict[trl][0])
            optimal_wait_dict[blk] = optimal_list
        return optimal_wait_dict

    def get_random_reward_time(self, session_dict):
        """
        used to deliver reward at random time post cue onset when reward delivery is not lick triggered
        makes a dictionary with block num as key and a list of random wait time for each trial as values
        randomly draws wait time
        """
        random_wait_dict = dict.fromkeys(range(self.total_blocks))
        for blk in session_dict:
            num_to_draw = len(session_dict[blk])
            drawn_times = np.random.uniform(0.5, self.max_wait_time, num_to_draw).tolist()
            random_wait_dict[blk] = [round(item, 1) for item in drawn_times]
        return random_wait_dict


if __name__ == '__main__':
    exp_config = utils.get_config('krave.experiment', 'config/exp1.json')
    session_dict = TaskConstruction("exp1", exp_config).get_session_structure()[1]
    random_dict = TaskConstruction("exp1", exp_config).get_random_reward_time(session_dict)
    print(random_dict)

