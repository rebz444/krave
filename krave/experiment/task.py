import time
import random
import math
import numpy as np
import statistics

from krave import utils
from krave.experiment import states
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.camera_trigger import CameraTrigger
from krave.output.data_writer import DataWriter

import sympy as sp
import pygame


def calculate_reward(time_wait):
    """
    reward function
    :param time_wait: time spent in waiting period
    :return: reward size in ul
    """
    return 2 * time_wait * math.exp(-time_wait / 10)


def calculate_optimal_wait_time(time_bg):
    """
    :param time_bg: bg time length
    :return: optimal wait time
    """
    t = sp.Symbol('t', real=True)
    r = 2 * t * sp.exp(-t / 10) / (t + time_bg)
    r_prime = r.diff(t)
    time_wait = sp.solve(r_prime, t)
    for i in time_wait:
        if i > 0:
            return round(i, 2)


class Task:
    def __init__(self, mouse, exp_name, calibrate=False, record=False):
        # experiment information
        self.mouse = mouse
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        self.calibrate = calibrate
        self.record = record

        # initiate hardware
        self.spout = Spout(self.mouse, self.exp_config, spout_name="1")
        self.visual = Visual(self.mouse, self.exp_config)
        self.camera_trigger = CameraTrigger(self.mouse, self.exp_config)
        self.data_writer = DataWriter(self.mouse, self.exp_name, self.exp_config)

        # session structure
        self.time_limit = self.exp_config['time_limit']
        self.total_blocks = self.exp_config['total_blocks']  # total number of blocks per session
        self.total_trials = self.exp_config['total_trials']  # median for total number of trials per session
        self.block_length_range = self.exp_config['block_length_range']
        self.blocks = self.exp_config['blocks']
        self.session_dict = dict.fromkeys(range(self.total_blocks))
        self.total_trial_num = None
        self.trial_list = None
        self.block_len = None

        # trial structure variables
        self.time_bg_range = self.exp_config['time_bg_range']
        self.consumption_time = self.exp_config['consumption_time']
        self.punishment_time = self.exp_config['punishment_time']
        self.max_wait_time = self.exp_config['max_wait_time']

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
        self.state = "in_background"
        self.lick_counter = 0
        self.total_reward = 0

    def get_config(self):
        """get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def get_session_structure(self):
        """
        Determines the session structure based on the number of blocks and lengths of avg bg time for each block
        makes a dictionary with block num as key and a list of background time for each trial as values
        time_bg_drawn from a uniform distribution with average of time_bg
        """
        trials_per_block = self.total_trials // self.total_blocks
        trials_per_block_min = trials_per_block - self.block_length_range
        trials_per_block_max = trials_per_block + self.block_length_range
        block_lengths = []
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

        for i, (l, t) in enumerate(zip(block_lengths, block_list)):
            low = t - self.time_bg_range
            high = t + self.time_bg_range
            self.session_dict[i] = np.random.uniform(low, high, l).tolist()
        print(f'length of each block: {block_lengths}')
        print(f'bg time of each block: {block_list}')
        print(f'total {self.total_trial_num} trials')
        print(f'session dict: {self.session_dict}')

    def start(self):
        """
        starts a session by getting session structure based on the type of training
        *************************currently only works for regular behavior session**************************************
        """
        self.session_start_time = time.time()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,session'
        self.data_writer.log(string)

        self.get_session_structure()
        self.start_block()

    def end(self):
        """end a session and shuts all systems"""
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,0,session'
        self.data_writer.log(string)

        self.visual.shutdown()
        self.spout.shutdown()
        self.data_writer.end()

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
        self.block_len = len(self.trial_list)
        self.time_bg = statistics.fmean(self.trial_list)

        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,block'
        self.data_writer.log(string)
        print(f"block {self.block_num} with bg_time {self.time_bg:.2f} sec "
              f"starts at {self.block_start_time - self.session_start_time:.2f} seconds")

        self.start_trial()

    def start_trial(self):
        """Starts a trial within a block"""
        self.block_trial_num += 1
        self.session_trial_num += 1
        self.time_bg_drawn = self.trial_list[self.block_trial_num]
        self.trial_start_time = time.time()
        self.state = "in_background"

        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg_drawn},nan,1,trial'
        self.data_writer.log(string)
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} bg_time "
              f"{self.time_bg_drawn:.2f}s starts at {self.trial_start_time - self.session_start_time:.2f} seconds")

    def end_trial(self):
        """ends a trial"""
        self.state = "trial_ends"
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg_drawn},nan,0,trial'
        self.data_writer.log(string)

    def log_lick(self):
        """log lick using data writer"""
        self.lick_counter += 1
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,lick'
        self.data_writer.log(string)
        print(f"lick {self.lick_counter} at {time.time() - self.session_start_time:.2f} seconds")

    def log_lick_ending(self):
        """log lick ending using data writer"""
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,0,lick'
        self.data_writer.log(string)

    def start_consumption(self):
        """starts consumption time, delivers reward, logs using data writer"""
        self.state = 'in_consumption'
        self.consumption_start_time = time.time()
        reward_size = calculate_reward(time.time() - self.cue_start_time)
        self.total_reward += reward_size
        self.spout.water_on(reward_size)
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},{reward_size},1,reward'
        self.data_writer.log(string)
        print(f'reward delivered, total reward is {self.total_reward:.2f} uL')

    def start_punishment(self):
        """starts punishment time, logs using data writer, trial does not restart"""
        self.state = 'in_punishment'
        self.punishment_start_time = time.time()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,punishment'
        self.data_writer.log(string)
        print('early lick, punishment')

    def end_punishment(self):
        """ends punishment time, logs using data writer, enters bg time"""
        self.state = 'in_background'
        self.trial_start_time = time.time()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,0,punishment'
        self.data_writer.log(string)
        print('start background time')

    def start_wait(self):
        """starts wait time, logs using data writer"""
        self.state = 'in_wait'
        print(self.state)
        self.visual.cue_on()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,visual'
        self.data_writer.log(string)
        self.cue_start_time = time.time()

    def test_test(self):
        if self.state == 'in_background':
            print(constants.IN_WAIT)

    def session(self):
        """regular behavior session"""
        self.start()
        try:
            if self.calibrate:
                self.spout.calibrate()
            while self.session_start_time + self.time_limit > time.time():
                if self.record:
                    self.camera_trigger.square_wave(self.data_writer)
                self.spout.water_cleanup()
                self.visual.cue_cleanup()

                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    self.log_lick()
                    if self.state == 'in_wait':
                        self.start_consumption()
                    elif self.state == 'in_background':
                        self.start_punishment()
                elif lick_change == -1:
                    self.log_lick_ending()

                if self.state == 'in_background' and time.time() > self.trial_start_time + self.time_bg_drawn:
                    self.start_wait()

                if self.state == 'in_consumption' \
                        and time.time() > self.consumption_start_time + self.consumption_time:
                    self.end_trial()

                if self.state == 'in_wait' and time.time() > self.cue_start_time + self.max_wait_time:
                    print('no lick, miss trial')
                    self.end_trial()

                if self.state == 'in_punishment' and time.time() > self.punishment_start_time + self.punishment_time:
                    self.end_punishment()

                if self.state == 'trial_ends':
                    if self.session_trial_num + 1 == self.total_trial_num:
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

    def shaping(self, time_bg, random_draw=False):
        """
        shaping with one bg_time
        :param time_bg:
        :param random_draw: default to false for shaping
        """
        self.time_bg = time_bg
        self.random_draw = random_draw
        self.start()
        self.start_trial()

        time_wait = calculate_optimal_wait_time(time_bg)
        reward_size = calculate_reward(time_wait)
        sol_duration = self.spout.calculate_duration(reward_size)
        print(f'time_bg = {time_bg}s, optimal leave time = {time_wait}s, reward = {reward_size}ul')

        try:
            if self.calibrate:
                self.spout.calibrate()
            while self.session_start_time + self.time_limit > time.time():
                if self.record:
                    self.camera_trigger.square_wave(self.data_writer)
                self.spout.water_cleanup()
                self.visual.cue_cleanup()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    self.lick_counter += 1
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,lick'
                    self.data_writer.log(string)
                elif lick_change == -1:
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,lick'
                    self.data_writer.log(string)

                if self.state == 'in_background' and time.time() > self.trial_start_time + time_bg:
                    self.state = 'waiting_time'
                    self.visual.cue_on()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,visual'
                    self.data_writer.log(string)
                    self.cue_start_time = time.time()
                if self.state == 'waiting_time' and time.time() > self.cue_start_time + time_wait:
                    self.state = 'in_consumption'
                    self.consumption_start_time = time.time()
                    self.total_reward += reward_size
                    self.spout.water_on(sol_duration)
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},{reward_size},1,reward'
                    self.data_writer.log(string)
                    print(f'reward delivered, total reward is {self.total_reward:.2f} uL')
                if self.state == 'in_consumption' and time.time() > self.consumption_start_time + self.consumption_time:
                    self.start_trial()
        finally:
            self.end()