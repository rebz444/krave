import time
import os
import pexpect

from krave import utils
from shutil import rmtree


class DataWriter:
    def __init__(self, mouse, exp_name, exp_config):
        self.mouse = mouse
        self.exp_name = exp_name
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]

        self.ip = self.hardware_config['desktop_ip']
        self.user = self.hardware_config['user_name']
        self.password = self.hardware_config['password']
        self.pi_suer_name = self.hardware_config['pi_user_name']

        self.datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.folder_name = self.mouse + '_' + self.datetime
        # self.data_write_path = os.path.join('/media', 'pi', 'rbz_data', self.folder_name)  # thumb drive
        self.data_write_path = os.path.join('/home', 'rebekahpi', 'Documents', 'behavior_data', self.folder_name)
        # path on pi
        print("path on pi: ", self.data_write_path)
        self.filename = "data_" + self.mouse + "_" + self.datetime + ".txt"
        # self.data_send_path = os.path.join('C:', 'Users', self.user, 'Documents', 'behavior_data')
        self.data_send_path = os.path.join('D:', 'behavior_data')
        self.f = None

        print("cwd: ", os.getcwd())
        os.system(f'sudo -u {self.pi_suer_name} mkdir -p ' + self.data_write_path)  # make dir for data write path
        os.chdir(self.data_write_path)
        os.system('sudo touch ' + self.filename)  # make the file for writing the data
        os.system('sudo chmod o+w ' + self.filename)  # add permission to write in the data file
        self.f = open(self.filename, 'w')  # open the file for writing
        info_fields = 'mouse,date,time,exp'
        self.f.write(info_fields + '\n')
        session_info = [self.mouse, self.datetime[0:10], self.datetime[11:19], self.exp_name]
        info_string = ','.join(session_info)
        self.f.write(info_string + '\n')
        data_fields = 'session_time,block_num,session_trial_num,block_trial_num,state,time_bg,reward_size,value,key'
        self.f.write('\n'.join(['# Data', data_fields, '']))

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

    def end(self, forward=False):
        self.f.close()
        if forward:
            os.chdir('..')
            os.chdir('..')
            # os.system('sudo chmod o-w ' + self.filename)
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
