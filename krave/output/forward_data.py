import os
from krave.helper import utils
import paramiko


def forward_and_delete_folders():
    """
    Forwards folders recursively from a source directory to a destination directory on a remote host using SSH,
    then deletes the forwarded folders from the source.
    """
    data_writer_config = utils.get_config('krave.output', 'data_writer_config.json')
    pi_data_dir = data_writer_config["pi_data_dir"]
    pc_data_dir = data_writer_config["pc_data_dir"]
    pc_ip = data_writer_config['pc_ip']
    pc_username = data_writer_config['pc_username']
    pc_password = data_writer_config['pc_password']

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=pc_ip, username=pc_username, password=pc_password)

    sftp = ssh.open_sftp()

    def _forward_and_delete_folder(source, dest):
        if not os.path.exists(source):
            print(f"Source directory does not exist: {source}")
            return

        try:
            sftp.mkdir(dest)
        except IOError:
            pass  # Directory might already exist

        for item in os.listdir(source):
            item_path = os.path.join(source, item)
            dest_path = os.path.join(dest, item)

            if os.path.isdir(item_path):
                _forward_and_delete_folder(item_path, dest_path)
            else:
                try:
                    sftp.put(item_path, dest_path)
                    os.remove(item_path)
                    print(f"Forwarded and deleted: {item_path}")
                except Exception as e:
                    print(f"Error processing {item_path}: {str(e)}")

        # Remove the now-empty source directory
        try:
            os.rmdir(source)
            print(f"Deleted empty directory: {source}")
        except OSError as e:
            print(f"Error deleting directory {source}: {str(e)}")

    try:
        _forward_and_delete_folder(pi_data_dir, pc_data_dir)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        sftp.close()
        ssh.close()

if __name__ == '__main__':
    forward_and_delete_folders()



