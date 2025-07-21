import os
from shutil import rmtree
from krave.helper import utils
import paramiko


class DataSender:
    """
    Handles secure file transfer (SFTP) of experiment data from the Raspberry Pi to a remote PC.
    Establishes SSH/SFTP connections and provides methods to send single or multiple directories.
    """
    def __init__(self):
        """
        Initialize the DataSender, set up SFTP/SSH connection using configuration from data_writer_config.json.
        """
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

    def send_dir(self, source_dir, dest_dir):
        """
        Send a specific directory from the Pi to the PC using SFTP.
        Transfers all files and subdirectories, then deletes the source directory on the Pi.
        Args:
            source_dir (str): Full path to the directory on the Pi.
            dest_dir (str): Full path to the destination directory on the PC.
        """
        try:
            self.sftp.mkdir(dest_dir)
        except IOError:
            # Directory might already exist, which is fine
            pass
        
        for dirpath, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                local_file = os.path.join(dirpath, filename)
                remote_file = os.path.join(dest_dir, os.path.relpath(local_file, source_dir))
                try:
                    self.sftp.put(local_file, remote_file)
                    print(f"Transferred: {local_file} to {remote_file}")
                except Exception as e:
                    print(f"Error transferring {local_file}: {str(e)}")
        self.delete_dir(source_dir)
    
    def delete_dir(self, source_dir):
        """
        Delete a directory and all its contents from the Pi after successful transfer.
        Args:
            source_dir (str): Full path to the directory to delete.
        """
        try:
            rmtree(source_dir)
            print(f"Deleted: {source_dir}")
        except Exception as e:
            print(f"Error deleting {source_dir}: {str(e)}")

    def send_all_dir(self):
        """
        Send all directories in the Pi data folder to the PC data folder.
        Calls send_dir for each directory, then shuts down the SFTP/SSH connection.
        """
        for dir in os.listdir(self.pi_data_dir):
            source_dir = os.path.join(self.pi_data_dir, dir)
            dest_dir = os.path.join(self.pc_data_dir, dir)
            self.send_dir(source_dir, dest_dir)
        self.shutdown()
    
    def shutdown(self):
        """
        Close the SFTP and SSH connections cleanly.
        """
        self.sftp.close()
        self.ssh.close()


if __name__ == '__main__':
    DataSender().send_all_dir()



