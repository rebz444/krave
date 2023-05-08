import time
import statistics

from krave import utils
from krave.experiment import states
from krave.experiment.task_construction import TaskConstruction
from krave.output.data_writer import DataWriter
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.hardware.spout import Spout
from krave.hardware.pi_camera import CameraPi


import pygame
import RPi.GPIO as GPIO


class Task:
    def __init__(self, mouse, exp_name, rig_name, training, record=False, forward_file=False):
        # experiment information
        exp_config = utils.get_config('krave', f'config/{exp_name}.json')
        hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]
        self.task_construction = TaskConstruction(exp_name, exp_config)
        session_structure = self.task_construction.get_session_structure()
        self.total_trial_num = session_structure[0]
        self.session_dict = session_structure[1]

        if training == 'shaping':
            self.auto_delivery = True
            self.random_wait_dict = self.task_construction.get_random_reward_time(self.session_dict)
        elif training == 'regular':
            self.auto_delivery = False
        else:
            raise Exception('Training type invalid')

        # initiate hardware
        self.data_writer = DataWriter(mouse, exp_name, training, exp_config, hardware_config, forward_file)
        self.visual = Visual(self.data_writer)
        self.trigger = Trigger(hardware_config, self.data_writer)
        self.spout = Spout(hardware_config, self.data_writer)
        self.camera = CameraPi()

        self.record = record

        # trial structure variables
        self.time_limit = exp_config['time_limit']
        self.max_reward = exp_config['max_reward']
        self.max_missed_trial = exp_config['max_missed_trial']
        self.consumption_time = exp_config['consumption_time']
        self.max_wait_time = exp_config['max_wait_time']
        self.time_enl = exp_config['enforced_no_lick_time']

        # session variables
        self.session_start_time = None
        self.block_start_time = None
        self.trial_start_time = None
        self.background_start_time = None
        self.background_end_time = None
        self.enl_start_time = None
        self.wait_start_time = None
        self.consumption_start_time = None

        self.trial_list = None
        self.random_list = None
        self.block_len = None
        self.block_num = -1
        self.block_trial_num = -1
        self.session_trial_num = -1

        self.time_bg = None  # average bg time of the block
        self.time_bg_drawn = None  # drawn bg time from uniform distribution
        self.time_wait_random = None
        self.state = states.IN_BACKGROUND
        self.lick_counter = 0
        self.total_reward = 0
        self.num_missed_trial = 0
        self.running = False

    def get_string_to_log(self, event):
        return f'{self.block_num},{self.session_trial_num},{self.block_trial_num},' \
               f'{self.state},{self.time_bg_drawn},' + event

    def start_session(self):
        """starts by getting session structure based on the type of training"""
        self.running = True
        self.camera.on()

        self.session_start_time = time.time()
        self.data_writer.log(self.get_string_to_log('nan,1,session'))

        self.start_block()

    def end_session(self):
        """end a session and shuts all systems"""
        self.data_writer.log(self.get_string_to_log('nan,0,session'))

        self.visual.shutdown()
        self.spout.shutdown()
        self.camera.shutdown()
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
        self.data_writer.log(self.get_string_to_log('nan,1,block'))

        self.block_num += 1
        self.block_trial_num = -1  # to make sure correct indexing because start_trial is called in this function
        self.trial_list = self.session_dict[self.block_num]
        if self.auto_delivery:
            self.random_list = self.random_wait_dict[self.block_num]
        self.block_len = len(self.trial_list)
        self.time_bg = statistics.fmean(self.trial_list)

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

        self.data_writer.log(self.get_string_to_log('nan,1,trial'))
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} bg_time "
              f"{self.time_bg_drawn:.2f}s starts at {self.trial_start_time - self.session_start_time:.2f} seconds")

        if self.auto_delivery:
            self.time_wait_random = self.random_list[self.block_trial_num]
            print(f'time_wait_random: {self.time_wait_random}')

        self.start_background()

    def end_trial(self):
        """
        ends a trial
        check session status to decide if to proceed
        starts a new block if trial is the last one in block
        else starts a new trial
        """
        self.data_writer.log(self.get_string_to_log('nan,0,trial'))
        self.check_session_status()
        if self.block_trial_num + 1 == self.block_len:
            self.start_block()
        else:
            self.start_trial()

    def start_background(self):
        """starts background time, sets bg_end_time, turns on visual cue,
        trial does not restart if repeated"""
        self.state = states.IN_BACKGROUND
        self.background_start_time = time.time()
        self.data_writer.log(self.get_string_to_log('nan,1,background'))
        print('background time starts')
        self.background_end_time = self.background_start_time + self.time_bg_drawn - self.time_enl
        self.visual.cue_on()

    def start_enforced_no_lick(self):
        """last 500ms of bg time is enforced no lick"""
        self.state = states.IN_ENFORCED_NO_LICK
        self.enl_start_time = time.time()
        self.data_writer.log(self.get_string_to_log('nan,1,enl'))
        print(f"ENL starts at {time.time() - self.trial_start_time:.2f} seconds")

    def start_wait(self):
        """starts wait time, turns off visual cue, logs using data writer"""
        self.state = states.IN_WAIT
        self.visual.cue_off()
        self.wait_start_time = time.time()
        print(self.state)
        self.data_writer.log(self.get_string_to_log('nan,1,wait'))

    def start_consumption(self):
        """starts consumption time, delivers reward, logs using data writer"""
        self.state = states.IN_CONSUMPTION
        self.consumption_start_time = time.time()
        time_waited = time.time() - self.wait_start_time
        reward_size = utils.calculate_reward(time.time() - self.wait_start_time)

        self.data_writer.log(self.get_string_to_log(f'{reward_size},1,consumption'))
        print(f'waited {time_waited:.2f}s, {reward_size:.2f}ul delivered, total is {self.total_reward:.2f}uL')

        self.total_reward += reward_size
        self.num_missed_trial = 0
        self.spout.calculate_pulses(reward_size)
        self.spout.send_continuous_pulse(self.spout.reward_pin)

    def check_session_status(self):
        if self.session_start_time + self.time_limit < time.time():
            print("time limit reached")
            self.running = False
        if self.total_reward >= self.max_reward:
            print('max_reward reached')
            self.running = False
        if self.session_trial_num + 1 == self.total_trial_num:
            print('total_trial_num reached')
            self.running = False
        if self.num_missed_trial >= self.max_missed_trial:
            print('max_missed_trial reached')
            self.running = False

    def run(self):
        """regular behavior session"""
        self.start_session()
        while self.running:
            if self.record:
                self.trigger.square_wave()

            self.spout.water_cleanup()
            lick_change = self.spout.lick_status_check()
            if lick_change == 1:
                self.lick_counter += 1
                print(f"lick {self.lick_counter} at {time.time() - self.trial_start_time:.2f} seconds")
                if not self.auto_delivery:
                    if self.state == states.IN_WAIT:
                        self.start_consumption()
                    elif self.state == states.IN_ENFORCED_NO_LICK:
                        self.start_enforced_no_lick()

            if self.state == states.IN_BACKGROUND and time.time() > self.background_end_time:
                self.start_enforced_no_lick()

            if self.state == states.IN_ENFORCED_NO_LICK and time.time() > self.enl_start_time + self.time_enl:
                self.start_wait()

            if self.state == states.IN_WAIT:
                if self.auto_delivery and time.time() > self.wait_start_time + self.time_wait_random:
                    self.start_consumption()
                elif not self.auto_delivery and time.time() > self.wait_start_time + self.max_wait_time:
                    print('no lick, missed trial')
                    self.num_missed_trial += 1
                    self.end_trial()

            if self.state == states.IN_CONSUMPTION \
                    and time.time() > self.consumption_start_time + self.consumption_time:
                self.end_trial()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('pygame quit')
                    self.running = False

        self.end_session()
