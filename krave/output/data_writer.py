import time
import os
import pexpect
import json

from shutil import rmtree


class DataWriter:
    def __init__(self, mouse, exp_name, training, rig, exp_config, hardware_config, forward_file):
        self.exp_config = exp_config
        self.hardware_config = hardware_config
        self.forward_file = forward_file

        self.date = time.strftime("%Y-%m-%d")
        self.time = time.strftime("%H-%M-%S")
        self.dir = self.date + '_' + self.time + '_' + mouse
        self.data_write_path = os.path.join('/home', 'pi', 'Documents', 'behavior_data', self.dir)
        print("path on pi: ", self.data_write_path)
        self.filename = "events_" + self.dir + ".txt"
        self.data_send_path = os.path.join('D:', 'behavior_data')

        self.ip = self.hardware_config['desktop_ip']
        self.user = self.hardware_config['username']
        self.password = self.hardware_config['password']
        self.pi_username = self.hardware_config['pi_username']

        os.system(f'sudo -u {self.pi_username} mkdir -p ' + self.data_write_path)  # make dir for data write path
        os.chdir(self.data_write_path)

        self.meta = {'mouse': mouse,
                     'date': self.date,
                     'time': self.time,
                     'exp': exp_name,
                     'training': training,
                     'rig': rig,
                     'pump_ul_per_turn': hardware_config['ul_per_turn']}

        os.system('sudo touch ' + self.filename)  # make the file for writing the data
        os.system('sudo chmod o+w ' + self.filename)  # add permission to write in the data file
        self.f = open(self.filename, 'w')  # open the file for writing
        data_fields = 'session_time,block_num,session_trial_num,block_trial_num,state,time_bg,reward_size,value,key'
        self.f.write(data_fields + '\n')

    def ssh(self, cmd, timeout=30, bg_run=False):
        """SSH'es to a host using the supplied credentials and executes a command.
        Throws an exception if the command doesn't return 0.
        bgrun: run command in the background"""

        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        if bg_run:
            options += ' -f'

        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.user, self.ip, options, cmd)
        child = pexpect.spawnu(ssh_cmd, timeout=timeout)  # spawnu for Python 3
        child.expect(['[Pp]assword: '])
        child.sendline(self.password)
        child.expect(pexpect.EOF)
        child.close()

    def scp(self, timeout=30, bg_run=False):
        """Scp's to a host using the supplied credentials and executes a command.
        Throws an exception if the command doesn't return 0.
        bgrun: run command in the background"""

        options = '-r -q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        if bg_run:
            options += ' -f'
        scp_cmd = 'scp %s %s %s@%s:%s' % (options, self.data_write_path, self.user, self.ip, self.data_send_path)
        print(scp_cmd)
        print(os.getcwd())
        child = pexpect.spawnu(scp_cmd, timeout=timeout)  # spawnu for Python 3
        child.expect(['[Pp]assword: '])
        child.sendline(self.password)
        child.expect(pexpect.EOF)
        child.close()
        return child.exitstatus

    def log(self, string):
        session_time = time.time()
        new_line = str(session_time) + ',' + string + '\n'
        self.f.write(new_line)

    def update_meta(self, session_data):
        self.meta = self.meta | session_data
        meta_path = os.path.join(self.data_write_path, "meta_" + self.dir + ".json")
        with open(meta_path, 'w') as json_file:
            json.dump(self.meta, json_file, indent=4)

    def end(self, session_data=None):
        self.f.close()
        self.update_meta(session_data)
        if self.forward_file:
            os.chdir('..')
            os.chdir('..')
            mkdir_command = 'if not exist %s mkdir %s' % (
                self.data_send_path.replace('/', '\\'), self.data_send_path.replace('/', '\\'))
            self.ssh(mkdir_command)

            if not self.scp():
                print('\nSuccessful file transfer to "%s"\nDeleting local file from pi.' % self.data_send_path)
                rmtree(self.data_write_path)
            else:
                print('connection back to desktop timed out')
        else:
            print(f'saved locally at {self.data_write_path}')

