import math
import random
import numpy as np

from scipy.stats import expon

from krave.helper import utils


def exponential(time_wait):
    return 2 * time_wait * math.exp(-time_wait / 10)


def stepped_sigmoid(time_wait):
    if 0 <= time_wait < 1:
        return 0
    elif 1 <= time_wait < 2:
        return 0.3
    elif 2 <= time_wait < 3:
        return 1.2
    elif 3 <= time_wait < 4:
        return 3.8
    elif 4 <= time_wait < 5:
        return 7.3
    elif 5 <= time_wait < 6:
        return 9.2
    elif 6 <= time_wait < 7:
        return 9.8
    elif 7 <= time_wait:
        return 10


def probability_boolean(prob):
    if random.random() < prob:
        return 1
    else:
        return 0


class Reward:
    def __init__(self, exp_config):
        function_mapping = {"stepped_sigmoid": stepped_sigmoid,
                            "exponential": exponential,
                            "cumulative": self.cumulative}

        self.exp_config = exp_config
        self.reward_function = function_mapping.get(self.exp_config['reward_function_name'])
        self.function_type = self.exp_config['reward_function_type']
        if self.function_type == 'probability':
            self.probability_dict = self.generate_probability_dict()

    def generate_probability_dict(self):
        time_array = np.arange(0, self.exp_config['max_time_wait'] + self.exp_config['time_step_size'],
                               self.exp_config['time_step_size'])
        probabilities = expon.cdf(time_array, 0, self.exp_config['scale']) * self.exp_config['max_probability']
        time_array = np.round(time_array, 1)
        probability_dict = {time_wait: prob for time_wait, prob in zip(time_array, probabilities)}
        return probability_dict

    def cumulative(self, time_waited):
        probability = self.probability_dict[time_waited]
        reward_magnitude = probability_boolean(probability) * self.exp_config['reward_size']
        return reward_magnitude

    def calculate_reward(self, time_waited):
        return self.reward_function(time_waited)


if __name__ == '__main__':
    exp_config = utils.get_config('krave', 'config/exp2_short.json')
    reward = Reward(exp_config)
    print(reward.probability_dict)
    for n in range(100):
        reward_size = reward.calculate_reward(2)
        print(reward_size)
