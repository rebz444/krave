import time
import os
import pexpect

from krave import utils


class DataWriter:
    def __init__(self, info, hardware_config):
        self.mouse = info.mouse
        self.exp_name = info.exp_name
        self.hardware_config = hardware_config

        self.ip = self.hardware_config['desk_ip']
        self.user = self.hardware_config['user_name']
        self.password = self.hardware_config['password']

        self.data_write_path = '/data/' + self.mouse  # path on pi
        self.datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = "data_" + self.datetime + ".txt"
        self.ssh_path = 'PycharmProjects/behavior_code/data/' + self.mouse  # Change to data save location on the pc
        self.data_send_path = 'C:/Users/' + self.user + '/' + self.ssh_path + '/'  # Path on pc

        print(os.getcwd())
        os.system('sudo -u pi mkdir -p ' + os.getcwd() + self.data_write_path)  # make dir for data write path
        os.chdir(os.getcwd() + self.data_write_path)  # change dir to data write path
        os.system('sudo touch ' + self.filename)  # make the file for writing the data
        os.system('sudo chmod o+w ' + self.filename)  # add permission to write in the data file
        self.f = open(self.filename, 'w')  # open the file for writing

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

    def scp(self, destination, timeout=30, bg_run=False):
        """Scp's to a host using the supplied credentials and executes a command.
        Throws an exception if the command doesn't return 0.
        bgrun: run command in the background"""

        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        if bg_run:
            options += ' -f'
        scp_cmd = 'scp %s %s %s@%s:%s' % (options, self.filename, self.user, self.ip, destination + self.filename)
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

    def end(self):
        self.f.close()
        os.system('sudo chmod o-w ' + self.filename)
        mkdir_command = 'if not exist %s mkdir %s' % (
            self.ssh_path.replace('/', '\\'), self.ssh_path.replace('/', '\\'))
        ssh(self.ip, mkdir_command, self.user, self.password)

        if not scp(self.ip, self.filename, self.data_send_path, self.user, self.password):
            print('\nSuccessful file transfer to "%s"\nDeleting local file from pi.' % self.data_send_path)
            os.remove(self.filename)
        else:
            print('connection back to desktop timed out')
