import time
import os
import json
import requests
from shutil import rmtree

from krave.helper import utils

from krave.ui.constants import PATHS

import paramiko


class DataWriter:
    def __init__(self, session_config, exp_config, hardware_config):
        self.session_config = session_config
        self.exp_config = exp_config
        self.hardware_config = hardware_config
        self.data_writer_config = utils.get_config('krave.output', 'data_writer_config.json')

        self.date = time.strftime("%Y-%m-%d")
        self.time = time.strftime("%H-%M-%S")
        self.dir = self.date + '_' + self.time + '_' + self.session_config['mouse']
        self.data_write_path = os.path.join(self.data_writer_config['pi_data_folder'], self.dir)
        self.data_send_path = os.path.join(self.data_writer_config['pc_data_folder'], self.dir)

        self.meta_name = "meta_" + self.dir + ".json"
        self.events_name = "events_" + self.dir + ".txt"
        self.events = None

        self.make_dir()
        self.make_meta()
        self.make_events()

    def make_dir(self):
        os.makedirs(self.data_write_path)

    def write_json(self, dict_to_save):
        meta_path = os.path.join(self.data_write_path, self.meta_name)
        with open(meta_path, "w") as f:
            json.dump(dict_to_save, f, indent=2)

    def make_meta(self):
        session_time = {"date": self.date, "time": self.time}
        self.session_config = session_time | self.session_config
        meta = {
            "session_config": self.session_config,
            "exp_config": self.exp_config,
            "hardware_config": self.hardware_config
        }
        self.write_json(meta)

    def update_meta(self, session_data):
        self.session_config |= session_data
        meta = {
            "session_config": self.session_config,
            "exp_config": self.exp_config,
            "hardware_config": self.hardware_config
        }
        self.write_json(meta)

    def make_events(self):
        events_path = os.path.join(self.data_write_path, self.events_name)

        with open(PATHS.COMMUNICATION, 'a') as file:
            file.write(events_path)

        self.events = open(events_path, 'w')
        data_fields = 'session_time,block_num,session_trial_num,block_trial_num,state,time_bg,reward_size,value,key'
        self.events.write(data_fields + '\n')

    def log(self, string):
        new_line = str(time.time()) + ',' + string + '\n'
        self.events.write(new_line)

        self.events.flush()
        os.fsync(self.events.fileno())

    def send_dir(self):
        pc_ip = self.data_writer_config['pc_ip']
        pc_username = self.data_writer_config['pc_username']
        pc_password = self.data_writer_config['pc_password']

        ssh_client = paramiko.SSHClient()  # Create the SSHClient object first
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Set the policy
        ssh_client.connect(hostname=pc_ip, username=pc_username, password=pc_password)

        sftp = ssh_client.open_sftp()
        sftp.mkdir(self.data_send_path)
        for dirpath, dirnames, filenames in os.walk(self.data_write_path):
            for filename in filenames:
                local_file = os.path.join(dirpath, filename)
                remote_file = os.path.join(self.data_send_path,
                                           os.path.relpath(local_file, self.data_write_path))
                sftp.put(local_file, remote_file)  # Transfer each file
        ssh_client.close()

    def post_on_slack(self):
        requests.post(url="https://hooks.slack.com/triggers/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",
                      json=self.session_config)

    def end(self, session_data=None):
        self.events.close()
        if session_data:
            self.update_meta(session_data)

        if self.session_config['forward_file']:
            try:
                self.send_dir()
                print(f'\nSuccessful file transfer to "{self.data_send_path}"\n')
                rmtree(self.data_write_path)
                print("Files deleted from local storage.")
            except Exception as e:
                print(f"Error transferring files: {e}")
                print(f'Files saved locally at {self.data_write_path}')
        else:
            print(f'Files saved locally at {self.data_write_path}')

        self.post_on_slack()
