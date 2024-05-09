import time
import statistics

from krave.helper.reward_functions import Reward
from krave.helper import states, utils
from krave.helper.task_construction import TaskConstruction
from krave.output.data_writer import DataWriter
from krave.hardware.visual import Visual
from krave.hardware.camera_basler import CameraBasler
from krave.hardware.spout import Spout
from krave.hardware.camera_pi import CameraPi
from krave.hardware.sound import Sound

import pygame
import RPi.GPIO as GPIO


class Task:
    def __init__(self, mouse, rig_name, training, trainer, record=False, forward_file=True):
        # experiment information
        self.exp_name = utils.get_exp_name(mouse)

        self.session_config = {"mouse": mouse, "exp": self.exp_name, "training": training, "rig": rig_name,
                               "trainer": trainer, "record": record, "forward_file": forward_file}
        self.exp_config = utils.get_config('krave', f'config/{self.exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]

        self.task_construction = TaskConstruction(self.exp_config)
        self.total_trial_num, self.session_dict = self.task_construction.get_session_structure()
        if self.session_config['training'] == 'shaping':
            self.random_wait_dict = self.task_construction.get_random_reward_time(self.session_dict)

        # initiate helpers
        self.data_writer = DataWriter(self.session_config, self.exp_config, self.hardware_config)
        self.reward = Reward(self.exp_config)
        self.visual = Visual(self.data_writer)
        self.trigger = CameraBasler(self.hardware_config, self.data_writer)
        self.spout = Spout(self.hardware_config, self.data_writer)
        self.camera = CameraPi()
        self.sound = Sound()

        # session variables
        self.session_start_time = None
        self.block_start_time = None
        self.trial_start_time = None
        self.background_start_time = None
        self.wait_start_time = None
        self.consumption_start_time = None

        self.trial_list = None
        self.random_list = None
        self.block_len = None
        self.block_num = -1
        self.block_trial_num = -1
        self.session_trial_num = -1

        self.running = False
        self.time_bg = None  # average bg time of the block
        self.time_bg_drawn = None  # drawn bg time from uniform distribution
        self.time_wait_random = None
        self.state = None
        self.ending_code = None

        self.lick_counter = 0
        self.total_reward = 0
        self.waited_times = []
        self.num_miss_trial = 0

    def status(self):
        return f'{self.block_num},{self.session_trial_num},{self.block_trial_num},' \
               f'{self.state},{self.time_bg_drawn},'

    def get_string(self, event):
        return self.status() + event

    def start_session(self):
        """starts camera for 20 sec to adjust position of the mouse before starting session"""
        self.camera.on()
        input(f"running {self.exp_name}, press Enter to start session ..")

        self.running = True
        self.session_start_time = time.time()
        self.data_writer.log(self.get_string('nan,1,session'))

        self.start_block()

    def end_session(self):
        """end a session and shuts all systems"""
        self.data_writer.log(self.get_string('nan,0,session'))
        self.sound.on()

        self.visual.shutdown(self.status())
        self.spout.shutdown()
        self.camera.shutdown()
        self.trigger.shutdown()
        GPIO.cleanup()
        print("GPIO cleaned up")

        if self.waited_times:
            avg_tw = round(sum(self.waited_times) / len(self.waited_times), 2)
        else:
            avg_tw = 0

        session_data = {
            'total_reward': round(self.total_reward, 2),
            'total_trial': self.session_trial_num,
            'avg_tw': avg_tw,
            'ending_code': self.ending_code
                        }
        self.data_writer.end(session_data)

    def start_block(self):
        """
        starts a block within a session
        pulls the number of trials in the block from session_dict
        pulls times for shaping tasks from optimal_dict
        starts the first trial of the block
        """
        self.block_start_time = time.time()
        self.data_writer.log(self.get_string('nan,1,block'))

        self.block_num += 1
        self.block_trial_num = -1  # to make sure correct indexing because start_trial is called in this function
        self.trial_list = self.session_dict[self.block_num]
        if self.session_config['training'] == "shaping":
            self.random_list = self.random_wait_dict[self.block_num]
        self.block_len = len(self.trial_list)
        self.time_bg = statistics.fmean(self.trial_list)

        print(f"block {self.block_num} with bg_time {self.time_bg:.2f} sec "
              f"starts at {self.block_start_time - self.session_start_time:.2f} seconds")

        self.start_trial()

    def end_block(self):
        self.data_writer.log(self.get_string('nan,0,block'))
        self.start_block()

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

        self.data_writer.log(self.get_string('nan,1,trial'))
        print(f"block {self.block_num} trial {self.block_trial_num, self.session_trial_num} bg_time "
              f"{self.time_bg_drawn:.2f}s starts at {self.trial_start_time - self.session_start_time:.2f} seconds")

        if self.session_config['training'] == "shaping":
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
        self.state = states.TRIAL_TRANSITION
        self.data_writer.log(self.get_string('nan,0,trial'))
        self.check_session_status()
        if self.running:
            if self.block_trial_num + 1 == self.block_len:
                self.end_block()
            else:
                self.start_trial()

    def start_background(self):
        """Starts background time, turns on visual cue, and sets end time for background period."""
        self.state = states.IN_BACKGROUND
        self.background_start_time = time.time()
        self.data_writer.log(self.get_string('nan,1,background'))
        print(self.state)
        self.visual.on(self.status())

    def start_wait(self):
        """starts wait time, turns off visual cue"""
        self.state = states.IN_WAIT
        self.visual.off(self.status())
        self.wait_start_time = time.time()
        print(self.state)
        self.data_writer.log(self.get_string('nan,1,wait'))

    def start_consumption(self):
        """starts consumption time, delivers reward, logs using data writer"""
        self.state = states.IN_CONSUMPTION
        self.consumption_start_time = time.time()
        time_waited = self.consumption_start_time - self.wait_start_time
        reward_size = self.reward.calculate_reward(round(time_waited, 1))
        self.waited_times.append(time_waited)
        self.total_reward += reward_size
        self.data_writer.log(self.get_string(f'{reward_size},1,consumption'))
        print(f'waited {time_waited:.2f}s, {reward_size:.2f}ul delivered, total is {self.total_reward:.2f}uL')

        self.num_miss_trial = 0  # resets miss trial count
        self.spout.calculate_pulses(reward_size, self.status())
        self.spout.send_continuous_pulse(self.status())

    def check_session_status(self):
        """check if session should end"""
        if time.time() > self.session_start_time + self.exp_config['max_time']:
            print("time limit reached")
            self.running = False
            self.ending_code = "time"
        elif self.total_reward >= self.exp_config['max_reward']:
            print('max_reward reached')
            self.running = False
            self.ending_code = "reward"
        elif self.session_trial_num + 1 == self.total_trial_num:
            print('total_trial_num reached')
            self.running = False
            self.ending_code = "trial"
        elif self.num_miss_trial >= self.exp_config['max_missed_trial']:
            print('max_missed_trial reached')
            self.running = False
            self.ending_code = "miss"
        else:
            self.running = True

    def handle_licks(self):
        self.spout.water_cleanup(self.status())
        lick_change = self.spout.lick_status_check(self.status())
        if lick_change == 1:
            self.lick_counter += 1
            print(f"lick {self.lick_counter} at {time.time() - self.trial_start_time:.2f} seconds")
            if self.session_config['training'] == "regular":
                if self.state == states.IN_BACKGROUND and self.exp_config['bg_punishment']:
                    self.start_background()
                elif self.state == states.IN_WAIT:
                    self.start_consumption()

    def handle_background_events(self):
        if time.time() > self.background_start_time + self.time_bg_drawn:
            self.start_wait()

    def handle_wait_events(self):
        if self.session_config['training'] == "shaping" and time.time() > self.wait_start_time + self.time_wait_random:
            self.start_consumption()
        elif self.session_config['training'] == "regular" \
                and time.time() > self.wait_start_time + self.exp_config['time_wait_max']:
            print('no lick, missed trial')
            self.num_miss_trial += 1
            self.end_trial()

    def handle_consumption_events(self):
        if time.time() > self.consumption_start_time + self.exp_config['time_consumption']:
            self.end_trial()

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('manual quit')
                self.running = False
                self.ending_code = "pygame"

    def run(self):
        self.start_session()
        while self.running:
            if self.session_config['record']:
                self.trigger.square_wave(self.status())

            self.handle_licks()
            self.handle_pygame_events()

            if self.state == states.IN_BACKGROUND:
                self.handle_background_events()

            if self.state == states.IN_WAIT:
                self.handle_wait_events()

            if self.state == states.IN_CONSUMPTION:
                self.handle_consumption_events()

        if not self.running:
            self.end_session()

