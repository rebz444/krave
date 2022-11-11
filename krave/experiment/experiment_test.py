import time
import random
import math

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.camera_trigger import CameraTrigger
from krave.output.data_writer import DataWriter

import numpy as np
import sympy as sp
import pygame


def calculate_reward(time_wait):
    return 2 * time_wait * math.exp(-time_wait / 10)


def calculate_optimal_wait_time(time_bg):
    t = sp.Symbol('t', real=True)
    r = 2 * t * sp.exp(-t / 10)/(t + time_bg)
    r_prime = r.diff(t)
    time_wait = sp.solve(r_prime, t)
    for i in time_wait:
        if i > 0:
            return round(i, 2)


class Task:
    def __init__(self, mouse, exp_name):
        self.mouse = mouse
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']

        self.spout = Spout(self.mouse, self.exp_config, spout_name="1")
        self.visual = Visual(self.mouse, self.exp_config)
        self.data_writer = DataWriter(self.mouse, self.exp_name, self.exp_config)
        self.camera_trigger = CameraTrigger(self.mouse, self.exp_config)

        self.time_limit = self.exp_config['time_limit']
        self.session_length = self.exp_config['session_length']  # number of blocks per session
        self.block_length_min = self.exp_config['block_length_min']  # min number of trials per block
        self.block_length_max = self.exp_config['block_length_max']  # max number of trials per block
        self.consumption_time = self.exp_config['consumption_time']
        self.punishment_time = self.exp_config['punishment_time']
        self.max_wait_time = self.exp_config['max_wait_time']

        self.session_start = None
        self.block_start = None
        self.trial_start = None
        self.block_num = 0
        self.block_trial_num = 0
        self.session_trial_num = 0
        self.block_list = np.zeros(self.session_length).tolist()
        self.block_lengths = np.zeros(self.session_length).tolist()
        self.block_len = None
        self.time_bg = None
        self.state = "in_background"

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def get_block_structure(self):
        block_types = list(self.exp_config['blocks'].values())
        block_start = random.choice(block_types)
        self.block_list[0] = block_start
        if block_start == block_types[0]:
            for i in range(self.session_length):
                if i % 2 == 0:
                    self.block_list[i] = block_start
                else:
                    self.block_list[i] = block_types[1]
        elif block_start == block_types[1]:
            for i in range(self.session_length):
                if i % 2 == 0:
                    self.block_list[i] = block_start
                else:
                    self.block_list[i] = block_types[0]
        for i in range(self.session_length):
            self.block_lengths[i] = random.randint(self.block_length_min, self.block_length_max)
        print(f'length of each block: {self.block_lengths}')
        print(f'bg time of each block: {self.block_list}')
        print(f'total {sum(self.block_lengths)} trials')

    def block_reset(self):
        self.block_len = self.block_lengths[self.block_num]
        self.time_bg = self.block_list[self.block_num]
        self.block_num += 1
        self.block_trial_num = 0
        self.block_start = time.time()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,block'
        self.data_writer.log(string)
        print(f"block {self.block_num} with bg_time {self.time_bg} sec "
              f"starts at {self.block_start - self.session_start:.2f} seconds")

    def trial_reset(self):
        self.block_trial_num += 1
        self.session_trial_num += 1
        self.trial_start = time.time()
        self.state = "in_background"
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,trial'
        self.data_writer.log(string)
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} starts "
              f"at {self.trial_start - self.session_start:.2f} seconds")

    def start(self):
        self.session_start = time.time()
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,1,session'
        self.data_writer.log(string)

        self.visual.initialize()
        self.visual.screen.fill((0, 0, 0))
        pygame.display.update()

    def end(self):
        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                 f'{self.time_bg},nan,0,session'
        self.data_writer.log(string)
        self.visual.shutdown()
        self.spout.shutdown()
        self.data_writer.end()

    def session(self, record=False):
        self.start()
        self.get_block_structure()
        self.block_reset()
        self.trial_reset()

        lick_counter = 0
        total_reward = 0
        cue_start = None
        consumption_start = None
        punishment_start = None

        try:
            while self.session_start + self.time_limit > time.time():
                if record:
                    self.camera_trigger.square_wave(self.data_writer)
                self.spout.water_cleanup()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,lick'
                    self.data_writer.log(string)
                    print(f"lick {lick_counter} at {time.time() - self.session_start:.2f} seconds")
                    if self.state == 'waiting_for_lick':
                        self.state = 'consuming_reward'
                        consumption_start = time.time()
                        reward_size = calculate_reward(time.time() - cue_start)
                        total_reward += reward_size
                        self.spout.water_on(reward_size)
                        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                                 f'{self.time_bg},{reward_size},1,reward'
                        self.data_writer.log(string)
                        print(f'reward delivered, total reward is {total_reward:.2f} uL')
                        self.visual.cue_off()
                        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                                 f'{self.time_bg},nan,0,visual'
                        self.data_writer.log(string)
                    elif self.state == 'in_background':
                        self.state = 'in_punishment'
                        punishment_start = time.time()
                        string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                                 f'{self.time_bg},nan,1,punishment'
                        self.data_writer.log(string)
                        print('early lick, punishment')
                elif lick_change == -1:
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,lick'
                    self.data_writer.log(string)

                if self.state == 'in_background' and time.time() > self.trial_start + self.time_bg:
                    self.state = 'waiting_for_lick'
                    self.visual.cue_on()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,visual'
                    self.data_writer.log(string)
                    cue_start = time.time()
                if self.state == 'consuming_reward' and time.time() > consumption_start + self.consumption_time:
                    self.trial_reset()
                if self.state == 'waiting_for_lick' and time.time() > cue_start + self.max_wait_time:
                    print('no lick, miss trial')
                    self.trial_reset()
                    self.visual.cue_off()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,visual'
                    self.data_writer.log(string)
                if self.state == 'in_punishment' and time.time() > punishment_start + self.punishment_time:
                    self.state = 'in_background'
                    self.trial_start = time.time()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,punishment'
                    self.data_writer.log(string)
                    print('start background time')

                if self.session_trial_num == sum(self.block_lengths):
                    break
                elif self.block_trial_num == self.block_len:
                    self.block_reset()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print('pygame quit')
                        break
        finally:
            self.end()

    def shaping(self, time_bg):
        self.start()
        self.trial_reset()

        lick_counter = 0
        total_reward = 0
        cue_start = None
        consumption_start = None

        time_to_wait = calculate_optimal_wait_time(time_bg)
        reward_size = calculate_reward(time_to_wait)
        print(f'time_bg = {time_bg}s, optimal leave time = {time_to_wait}s, reward = {reward_size}ul')

        try:
            while self.session_start + self.time_limit > time.time():
                self.spout.water_cleanup()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,lick'
                    self.data_writer.log(string)
                elif lick_change == -1:
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,lick'
                    self.data_writer.log(string)

                if self.state == 'in_background' and time.time() > self.trial_start + time_bg:
                    self.state = 'waiting_time'
                    self.visual.cue_on()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,1,visual'
                    self.data_writer.log(string)
                    cue_start = time.time()
                if self.state == 'waiting_time' and time.time() > cue_start + time_to_wait:
                    self.state = 'consuming_reward'
                    consumption_start = time.time()
                    total_reward += reward_size
                    self.spout.water_on(reward_size)
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},{reward_size},1,reward'
                    self.data_writer.log(string)
                    print(f'reward delivered, total reward is {total_reward:.2f} uL')
                    self.visual.cue_off()
                    string = f'{self.block_num},{self.session_trial_num},{self.block_trial_num},{self.state},' \
                             f'{self.time_bg},nan,0,visual'
                    self.data_writer.log(string)
                if self.state == 'consuming_reward' and time.time() > consumption_start + self.consumption_time:
                    self.trial_reset()
        finally:
            self.end()

    def test_reward_optimal(self, time_bg):
        time_wait = calculate_optimal_wait_time(time_bg)
        print('optimal wait time is: ', time_wait)
        reward_size = calculate_reward(time_wait)
        print('reward size: ', reward_size)

    def calibrate_spout(self):
        print('calibrating port')
        open_time = 0.009
        total_open_time = 0
        for _ in range(50):
            self.spout.water_on(open_time)
            time.sleep(open_time)
            total_open_time += open_time
            self.spout.water_off()
            time.sleep(0.2)
        self.spout.shutdown()
        print(f'total water open time {total_open_time}s')

