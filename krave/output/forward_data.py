import os
from shutil import rmtree
from krave.helper import utils
import paramiko


class DataForward:
    def __init__(self):
        self.data_writer_config = utils.get_config('krave.output', 'data_writer_config.json')
        self.pi_data_dir = self.data_writer_config["pi_data_folder"]
        self.pc_data_dir = self.data_writer_config["pc_data_folder"]

        pc_ip = self.data_writer_config['pc_ip']
        pc_username = self.data_writer_config['pc_username']
        pc_password = self.data_writer_config['pc_password']

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=pc_ip, username=pc_username, password=pc_password)

        self.sftp = self.ssh.open_sftp()

    def create_remote_dir(self, path):
        try:
            self.sftp.mkdir(path)
        except IOError:
            # Directory might already exist, which is fine
            pass

    def process_dir(self):
        try:
            for dir in os.listdir(self.pi_data_dir):
                source_dir = os.path.join(self.pi_data_dir, dir)
                dest_dir = os.path.join(self.pc_data_dir, dir)

                self.create_remote_dir(dest_dir)

                for dirpath, dirnames, filenames in os.walk(source_dir):
                    for dirname in dirnames:
                        remote_dir = os.path.join(dest_dir, os.path.relpath(os.path.join(dirpath, dirname), source_dir))
                        self.create_remote_dir(remote_dir)

                    for filename in filenames:
                        local_file = os.path.join(dirpath, filename)
                        remote_file = os.path.join(dest_dir, os.path.relpath(local_file, source_dir))
                        try:
                            self.sftp.put(local_file, remote_file)
                            print(f"Transferred: {local_file} to {remote_file}")
                        except Exception as e:
                            print(f"Error transferring {local_file}: {str(e)}")

                try:
                    rmtree(source_dir)
                    print(f"Deleted: {source_dir}")
                except Exception as e:
                    print(f"Error deleting {source_dir}: {str(e)}")

        finally:
            self.sftp.close()
            self.ssh.close()


if __name__ == '__main__':
    DataForward().process_dir()



