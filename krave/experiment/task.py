import time
import random
import numpy as np
import statistics
import os

from krave import utils
from krave.experiment import states
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.output.data_writer import DataWriter

import pygame
import RPi.GPIO as GPIO


class Task:
    def __init__(self, mouse, exp_name, training, record=False, forward_file=False):
        # experiment information
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{self.exp_name}.json')
        self.record = record

        if training == 'shaping':
            self.auto_delivery = True
        elif training == 'regular':
            self.auto_delivery = False
        else:
            raise Exception('Training type invalid')

        # initiate hardware
        self.spout = Spout(self.exp_config, spout_name="1")
        self.visual = Visual(self.exp_config)
        self.trigger = Trigger(self.exp_config)
        self.data_writer = DataWriter(mouse, exp_name, training, self.exp_config, forward_file)

        # session structure
        self.time_limit = self.exp_config['time_limit']
        self.max_reward = self.exp_config['max_reward']
        self.total_blocks = self.exp_config['total_blocks']  # total number of blocks per session
        self.total_trials_median = self.exp_config['total_trials_median']  # median number of trials per session
        self.block_length_range = self.exp_config['block_length_range']
        self.blocks = self.exp_config['blocks']
        self.session_dict = dict.fromkeys(range(self.total_blocks))
        self.optimal_dict = dict.fromkeys(range(self.total_blocks))
        self.total_trial_num = None
        self.trial_list = None
        self.optimal_list = None
        self.block_len = None

        # trial structure variables
        self.time_bg_range = self.exp_config['time_bg_range']
        self.consumption_time = self.exp_config['consumption_time']
        self.punishment_time = self.exp_config['punishment_time']
        self.max_wait_time = self.exp_config['max_wait_time']
        self.wait_time_step_size = self.exp_config['wait_time_step_size']

        # session variables
        self.session_start_time = None
        self.block_start_time = None
        self.trial_start_time = None
        self.cue_start_time = None
        self.consumption_start_time = None
        self.punishment_start_time = None

        self.block_num = -1
        self.block_trial_num = -1
        self.session_trial_num = -1
        self.time_bg = None  # average bg time of the block
        self.time_bg_drawn = None  # drawn bg time from uniform distribution
        self.time_wait_optimal = None
        self.state = states.IN_BACKGROUND
        self.lick_counter = 0
        self.total_reward = 0

    def get_session_structure(self):
        """
        Determines the session structure based on the number of blocks and lengths of avg bg time for each block
        makes a dictionary with block num as key and a list of background time for each trial as values
        time_bg_drawn from a uniform distribution with average of time_bg
        """
        trials_per_block = self.total_trials_median // self.total_blocks
        trials_per_block_min = trials_per_block - self.block_length_range
        trials_per_block_max = trials_per_block + self.block_length_range
        block_lengths = []

        # make two block types alternate
        for i in range(self.total_blocks):
            block_lengths.append(random.randint(trials_per_block_min, trials_per_block_max))
        self.total_trial_num = sum(block_lengths)
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
        for i, (l, t) in enumerate(zip(block_lengths, block_list)):
            low = t - t * self.time_bg_range
            high = t + t * self.time_bg_range
            drawn_times = np.random.uniform(low, high, l).tolist()
            drawn_times = [round(item, 1) for item in drawn_times]
            self.session_dict[i] = drawn_times
            count += len(drawn_times)

        if count != self.total_trial_num:
            raise Exception('Missing time_bg!')

        print(f'length of each block: {block_lengths}')
        print(f'bg time of each block: {block_list}')
        print(f'{self.total_trial_num} trials total')

    def get_wait_time_optimal(self):
        """
        makes a dictionary with block num as key and a list of optimal wait time for each trial as values
        runs for shaping tasks when reward delivery is not lick triggered
        """
        path = os.path.join('/home', 'pi', 'Documents', 'behavior_code', 'krave', 'experiment', 'config')
        filename = self.exp_name + '_optimal_value_dict.pkl'
        optimal_value_dict = utils.load_pickle_as_dict(path, filename)
        print(optimal_value_dict)
        for blk in self.session_dict:
            optimal_list = []
            for trl in self.session_dict[blk]:
                optimal_list.append(optimal_value_dict[trl][0])
            self.optimal_dict[blk] = optimal_list

    def get_string_to_log(self, event):
        return f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},{self.time_bg},' + event

    def start(self):
        """starts a session by getting session structure based on the type of training"""
        self.get_session_structure()
        if self.auto_delivery:
            self.get_wait_time_optimal()

        self.start_session()
        self.start_block()

    def end(self):
        """end a session and shuts all systems"""
        string = self.get_string_to_log('nan,0,session')
        self.data_writer.log(string)

        self.visual.shutdown()
        self.spout.water_off()
        self.trigger.shutdown()
        self.data_writer.end()

        GPIO.cleanup()

    def start_session(self):
        self.session_start_time = time.time()
        string = self.get_string_to_log('nan,1,session')
        self.data_writer.log(string)

    def start_block(self):
        """
        starts a block within a session
        determines number of trials in the block and avg bg time
        starts the first trial of the block
        """
        self.block_num += 1
        self.block_trial_num = -1  # to make sure correct indexing because start_trial is called in this function
        self.block_start_time = time.time()
        self.trial_list = self.session_dict[self.block_num]
        if self.auto_delivery:
            self.optimal_list = self.optimal_dict[self.block_num]
        self.block_len = len(self.trial_list)
        self.time_bg = statistics.fmean(self.trial_list)

        string = self.get_string_to_log('nan,1,block')
        self.data_writer.log(string)
        print(f"block {self.block_num} with bg_time {self.time_bg:.2f} sec "
              f"starts at {self.block_start_time - self.session_start_time:.2f} seconds")

        self.start_trial()

    def log_lick(self):
        """logs lick using data writer"""
        print(f"lick {self.lick_counter} at {time.time() - self.session_start_time:.2f} seconds")
        self.lick_counter += 1
        string = self.get_string_to_log('nan,1,lick')
        self.data_writer.log(string)

    def log_lick_ending(self):
        """logs lick ending using data writer"""
        string = self.get_string_to_log('nan,0,lick')
        self.data_writer.log(string)

    def start_trial(self):
        """Starts a trial within a block"""
        self.block_trial_num += 1
        self.session_trial_num += 1
        self.time_bg_drawn = self.trial_list[self.block_trial_num]
        if self.auto_delivery:
            self.time_wait_optimal = self.optimal_list[self.block_trial_num]
        self.trial_start_time = time.time()
        self.state = states.IN_BACKGROUND

        string = self.get_string_to_log('nan,1,trial')
        self.data_writer.log(string)
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} bg_time "
              f"{self.time_bg_drawn:.2f}s starts at {self.trial_start_time - self.session_start_time:.2f} seconds")
        if self.auto_delivery:
            print(f'time_wait_optimal: {self.time_wait_optimal}')

    def end_trial(self):
        """ends a trial"""
        self.state = states.TRIAL_ENDS
        string = self.get_string_to_log('nan,0,trial')
        self.data_writer.log(string)

    def start_consumption(self):
        """starts consumption time, delivers reward, logs using data writer"""
        self.state = states.IN_CONSUMPTION
        self.consumption_start_time = time.time()
        reward_size = utils.calculate_reward(time.time() - self.cue_start_time)
        self.total_reward += reward_size
        self.spout.water_on(reward_size)

        string = self.get_string_to_log(f'{reward_size},1,reward')
        self.data_writer.log(string)
        print(f'reward delivered, total reward is {self.total_reward:.2f} uL')

    def start_punishment(self):
        """starts punishment time, logs using data writer, trial does not restart"""
        self.state = states.IN_PUNISHMENT
        self.punishment_start_time = time.time()

        string = self.get_string_to_log('nan,1,punishment')
        self.data_writer.log(string)
        print('early lick, punishment')

    def end_punishment(self):
        """ends punishment time, logs using data writer, enters bg time"""
        self.state = states.IN_BACKGROUND
        self.trial_start_time = time.time()

        string = self.get_string_to_log('nan,0,punishment')
        self.data_writer.log(string)
        print('start background time')

    def start_wait(self):
        """starts wait time, flash visual cue, logs using data writer"""
        self.state = states.IN_WAIT
        print(self.state)
        self.visual.cue_on()

        string = self.get_string_to_log('nan,1,wait')
        self.data_writer.log(string)
        string = self.get_string_to_log('nan,1,visual')
        self.data_writer.log(string)
        self.cue_start_time = time.time()

    def run(self):
        """regular behavior session"""
        self.start()
        try:
            while self.session_start_time + self.time_limit > time.time():
                self.spout.water_cleanup()
                self.visual.cue_cleanup()
                if self.record:
                    self.trigger.square_wave(self.data_writer)
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    self.log_lick()
                    if not self.auto_delivery:
                        if self.state == states.IN_WAIT:
                            self.start_consumption()
                        elif self.state == states.IN_BACKGROUND:
                            self.start_punishment()
                elif lick_change == -1:
                    self.log_lick_ending()

                if self.state == states.IN_BACKGROUND and time.time() > self.trial_start_time + self.time_bg_drawn:
                    self.start_wait()

                if self.state == states.IN_WAIT:
                    if self.auto_delivery and time.time() > self.cue_start_time + self.time_wait_optimal:
                        self.start_consumption()
                    elif not self.auto_delivery and time.time() > self.cue_start_time + self.max_wait_time:
                        print('no lick, miss trial')
                        self.end_trial()

                if self.state == states.IN_CONSUMPTION \
                        and time.time() > self.consumption_start_time + self.consumption_time:
                    self.end_trial()

                if self.state == states.IN_PUNISHMENT \
                        and time.time() > self.punishment_start_time + self.punishment_time:
                    self.end_punishment()

                # session ends if total num of trials is reached, or if reward received is larger than max reward
                if self.state == states.TRIAL_ENDS:
                    if self.session_trial_num + 1 == self.total_trial_num:
                        print('total_trial_num reached')
                        break
                    elif self.total_reward >= self.max_reward:
                        print('max_reward reached')
                        break
                    elif self.block_trial_num + 1 == self.block_len:
                        self.start_block()
                    else:
                        self.start_trial()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print('pygame quit')
                        break
        finally:
            self.end()
