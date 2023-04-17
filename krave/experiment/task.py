import time
import random
import numpy as np
import statistics
import os

from krave import utils
from krave.experiment import states
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.hardware.spout import Spout
from krave.output.data_writer import DataWriter

import pygame
import RPi.GPIO as GPIO


class Task:
    def __init__(self, mouse, exp_name, rig_name, training, record=False, forward_file=False):
        # experiment information
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{self.exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]
        self.record = record

        if training == 'shaping':
            self.auto_delivery = True
        elif training == 'regular':
            self.auto_delivery = False
        else:
            raise Exception('Training type invalid')

        # initiate hardware
        self.visual = Visual(self.exp_config)
        self.trigger = Trigger(self.hardware_config)
        self.spout = Spout(self.hardware_config)
        self.data_writer = DataWriter(mouse, exp_name, training,
                                      self.exp_config, self.hardware_config, forward_file)

        # session structure
        self.time_limit = self.exp_config['time_limit']
        self.max_reward = self.exp_config['max_reward']
        self.total_blocks = self.exp_config['total_blocks']  # total number of blocks per session
        self.total_trials_median = self.exp_config['total_trials_median']  # median number of trials per session
        self.block_length_range = self.exp_config['block_length_range']
        self.blocks = self.exp_config['blocks']
        self.session_dict = dict.fromkeys(range(self.total_blocks))
        self.optimal_wait_dict = dict.fromkeys(range(self.total_blocks))
        self.random_wait_dict = dict.fromkeys(range(self.total_blocks))
        self.total_trial_num = None
        self.trial_list = None
        self.optimal_list = None
        self.random_list = None
        self.block_len = None

        # trial structure variables
        self.time_bg_range = self.exp_config['time_bg_range']
        self.consumption_time = self.exp_config['consumption_time']
        self.max_wait_time = self.exp_config['max_wait_time']
        self.wait_time_step_size = self.exp_config['wait_time_step_size']
        self.time_enl = self.exp_config['enforced_no_lick_time']

        # session variables
        self.session_start_time = None
        self.block_start_time = None
        self.trial_start_time = None
        self.background_start_time = None
        self.background_end_time = None
        self.enl_start_time = None
        self.wait_start_time = None
        self.consumption_start_time = None

        self.block_num = -1
        self.block_trial_num = -1
        self.session_trial_num = -1
        self.time_bg = None  # average bg time of the block
        self.time_bg_drawn = None  # drawn bg time from uniform distribution
        self.time_wait_optimal = None
        self.time_wait_random = None
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
        used to deliver reward at optimal wait time when reward delivery is not lick triggerd
        makes a dictionary with block num as key and a list of optimal wait time for each trial as values
        pulls optimal wait time from saved pickle
        """
        path = os.path.join('/home', 'pi', 'Documents', 'behavior_code', 'krave', 'experiment', 'config')
        filename = self.exp_name + '_optimal_value_dict.pkl'
        optimal_value_dict = utils.load_pickle_as_dict(path, filename)
        for blk in self.session_dict:
            optimal_list = []
            for trl in self.session_dict[blk]:
                optimal_list.append(optimal_value_dict[trl][0])
            self.optimal_wait_dict[blk] = optimal_list

    def get_random_reward_time(self):
        """
        used to deliver reward at random time post cue onset when reward delivery is not lick triggered
        makes a dictionary with block num as key and a list of random wait time for each trial as values
        randomly draws wait time
        """
        for blk in self.session_dict:
            num_to_draw = len(self.session_dict[blk])
            drawn_times = np.random.uniform(0.5, self.max_wait_time, num_to_draw).tolist()
            self.random_wait_dict[blk] = [round(item, 1) for item in drawn_times]

    def get_string_to_log(self, event):
        return f'{self.block_num},{self.session_trial_num},{self.block_trial_num},' \
               f'{self.state},{self.time_bg_drawn},' + event

    def start_session(self):
        """starts by getting session structure based on the type of training"""
        self.visual.initiate()
        self.session_start_time = time.time()
        self.get_session_structure()
        if self.auto_delivery:
            self.get_wait_time_optimal()
            self.get_random_reward_time()

        string = self.get_string_to_log('nan,1,session')
        self.data_writer.log(string)

        self.start_block()

    def end_session(self):
        """end a session and shuts all systems"""
        string = self.get_string_to_log('nan,0,session')
        self.data_writer.log(string)

        self.visual.shutdown()
        self.spout.shutdown()
        self.trigger.shutdown()
        self.data_writer.end()

        GPIO.cleanup()
        print("GPIO cleaned up")

    def start_block(self):
        """
        starts a block within a session
        pulls the number of trials in the block from session_dict
        pulls times for shaping tasks from optimal_dict
        starts the first trial of the block
        """
        self.block_start_time = time.time()

        self.block_num += 1
        self.block_trial_num = -1  # to make sure correct indexing because start_trial is called in this function
        self.trial_list = self.session_dict[self.block_num]
        if self.auto_delivery:
            self.optimal_list = self.optimal_wait_dict[self.block_num]
            self.random_list = self.random_wait_dict[self.block_num]
        self.block_len = len(self.trial_list)
        self.time_bg = statistics.fmean(self.trial_list)

        string = self.get_string_to_log('nan,1,block')
        self.data_writer.log(string)
        print(f"block {self.block_num} with bg_time {self.time_bg:.2f} sec "
              f"starts at {self.block_start_time - self.session_start_time:.2f} seconds")

        self.start_trial()

    def start_trial(self):
        """
        Starts a trial within a block
        gets background time for the trial
        gets optimal reward time for shaping task
        """
        self.trial_start_time = time.time()
        self.block_trial_num += 1
        self.session_trial_num += 1
        self.time_bg_drawn = self.trial_list[self.block_trial_num]

        string = self.get_string_to_log('nan,1,trial')
        self.data_writer.log(string)
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} bg_time "
              f"{self.time_bg_drawn:.2f}s starts at {self.trial_start_time - self.session_start_time:.2f} seconds")

        if self.auto_delivery:
            self.time_wait_optimal = self.optimal_list[self.block_trial_num]
            self.time_wait_random = self.random_list[self.block_trial_num]
            print(f'time_wait_optimal: {self.time_wait_optimal}')
            print(f'time_wait_random: {self.time_wait_random}')

        self.start_background()

    def end_trial(self):
        """ends a trial"""
        self.state = states.TRIAL_ENDS
        string = self.get_string_to_log('nan,0,trial')
        self.data_writer.log(string)

    def log_lick(self):
        """logs lick using data writer"""
        print(f"lick {self.lick_counter} at {time.time() - self.trial_start_time:.2f} seconds")
        self.lick_counter += 1
        string = self.get_string_to_log('nan,1,lick')
        self.data_writer.log(string)

    def log_lick_ending(self):
        """logs lick ending using data writer"""
        string = self.get_string_to_log('nan,0,lick')
        self.data_writer.log(string)

    def start_background(self):
        """starts background time, sets bg_end_time, turns on visual cue,
        trial does not restart if repeated"""
        self.state = states.IN_BACKGROUND
        self.background_start_time = time.time()
        self.background_end_time = self.background_start_time + self.time_bg_drawn - self.time_enl

        string = self.get_string_to_log('nan,1,background')
        self.data_writer.log(string)
        print('background time starts')

        self.visual.cue_on()
        string = self.get_string_to_log('nan,1,visual')
        self.data_writer.log(string)

    def start_enforced_no_lick(self):
        """last 500ms of bg time is enforced no lick, mouse """
        self.state = states.IN_ENFORCED_NO_LICK
        self.enl_start_time = time.time()

        string = self.get_string_to_log('nan,1,enl')
        self.data_writer.log(string)
        print(f"ENL starts at {time.time() - self.trial_start_time:.2f} seconds")

    def start_wait(self):
        """starts wait time, turns off visual cue, logs using data writer"""
        self.state = states.IN_WAIT
        self.wait_start_time = time.time()
        print(self.state)
        string = self.get_string_to_log('nan,1,wait')
        self.data_writer.log(string)

        self.visual.cue_off()
        string = self.get_string_to_log('nan,0,visual')
        self.data_writer.log(string)

    def start_consumption(self):

        """starts consumption time, delivers reward, logs using data writer"""
        self.state = states.IN_CONSUMPTION
        self.consumption_start_time = time.time()
        reward_size = utils.calculate_reward(time.time() - self.wait_start_time)
        self.total_reward += reward_size
        self.spout.calculate_pulses(reward_size)
        self.spout.send_continuous_pulse(self.spout.reward_pin)

        string = self.get_string_to_log(f'{reward_size},1,reward')
        self.data_writer.log(string)
        print(f'{reward_size:.2f} ul delivered, total reward is {self.total_reward:.2f} uL')

    def run(self):
        """regular behavior session"""
        self.start_session()
        try:
            while self.session_start_time + self.time_limit > time.time():
                self.spout.cleanup()
                if self.record:
                    self.trigger.square_wave(self.data_writer)
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    self.log_lick()
                    if not self.auto_delivery:
                        if self.state == states.IN_WAIT:
                            self.start_consumption()
                        elif self.state == states.IN_ENFORCED_NO_LICK:
                            self.start_enforced_no_lick()
                elif lick_change == -1:
                    self.log_lick_ending()

                if self.state == states.IN_BACKGROUND and time.time() > self.background_end_time:
                    self.start_enforced_no_lick()

                if self.state == states.IN_ENFORCED_NO_LICK and time.time() > self.enl_start_time + self.time_enl:
                    self.start_wait()

                if self.state == states.IN_WAIT:
                    if self.auto_delivery and time.time() > self.wait_start_time + self.time_wait_random:
                        self.start_consumption()
                    elif not self.auto_delivery and time.time() > self.wait_start_time + self.max_wait_time:
                        print('no lick, miss trial')
                        self.end_trial()

                if self.state == states.IN_CONSUMPTION \
                        and time.time() > self.consumption_start_time + self.consumption_time:
                    self.end_trial()

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
            self.end_session()
