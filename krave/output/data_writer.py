import time
import os
import json
import requests
from shutil import rmtree

from krave.helper import utils
from krave.ui.constants import PATHS
from krave.output.data_sender import DataSender

import paramiko


class DataWriter:
    def __init__(self, session_config, exp_config, hardware_config):
        """
        Initialize the DataWriter for a session.
        Sets up paths, configuration, and creates necessary files for data logging.
        """
        self.session_config = session_config
        self.exp_config = exp_config
        self.hardware_config = hardware_config
        self.data_writer_config = utils.get_config('krave.output', 'data_writer_config.json')
        self.data_sender = DataSender()

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
        """
        Create the directory for writing session data.
        """
        os.makedirs(self.data_write_path, exist_ok=True)

    def write_json(self, dict_to_save):
        """
        Write a dictionary as JSON to the session's meta file.
        """
        meta_path = os.path.join(self.data_write_path, self.meta_name)
        with open(meta_path, "w") as f:
            json.dump(dict_to_save, f, indent=2)

    def make_meta(self):
        """
        Create the meta file for the session, including session, experiment, and hardware config.
        """
        session_time = {"date": self.date, "time": self.time}
        self.session_config = session_time | self.session_config
        meta = {
            "session_config": self.session_config,
            "exp_config": self.exp_config,
            "hardware_config": self.hardware_config
        }
        self.write_json(meta)

    def update_meta(self, session_data):
        """
        Update the meta file with additional session data (e.g., summary stats).
        """
        self.session_config |= session_data
        meta = {
            "session_config": self.session_config,
            "exp_config": self.exp_config,
            "hardware_config": self.hardware_config
        }
        self.write_json(meta)

    def make_events(self):
        """
        Create the events file for logging trial/block/session events.
        """
        events_path = os.path.join(self.data_write_path, self.events_name)

        with open(PATHS.COMMUNICATION, 'a') as file:
            file.write(events_path)

        self.events = open(events_path, 'w')
        data_fields = 'session_time,block_num,session_trial_num,block_trial_num,state,time_bg,reward_size,value,key'
        self.events.write(data_fields + '\n')

    def log(self, string):
        """
        Log a string (event) to the events file, with a timestamp.
        """
        new_line = str(time.time()) + ',' + string + '\n'
        self.events.write(new_line)
        self.events.flush()
        os.fsync(self.events.fileno())

    def post_on_slack(self):
        """
        Post session configuration to a Slack webhook for notification.
        """
        try:
            requests.post(url="https://hooks.slack.com/triggers/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",
                          json=self.session_config)
        except Exception as e:
            print(f"Error posting on slack: {e}")

    def end(self, session_data=None):
        """
        Finalize the session: close files, update meta, transfer files if needed, and post to Slack.
        Ensures the events file is always closed, even if an error occurs.
        """
        try:
            if session_data:
                self.update_meta(session_data)
        finally:
            if hasattr(self, 'events') and self.events:
                self.events.close()

        self.post_on_slack()

        if self.session_config['forward_file']:
            self.data_sender.send_dir(self.data_write_path, self.data_send_path)
        else:
            print(f'Files saved locally at {self.data_write_path}')
        self.data_sender.shutdown()
