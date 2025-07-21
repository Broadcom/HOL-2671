import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import paramiko
from pyVmomi import vim, vmodl
import socket


def runRemoteScript(hostname, username, password, command):
    # Establish SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, username=username, password=password)

    try:

        # Execute command to check if file exists
        stdin, stdout, stderr = ssh_client.exec_command(f"{command}")

        exit_status = stdout.channel.recv_exit_status()

        # Check if any output was returned
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if exit_status == 0:
            print(f"INFO: Command executed successfully: {output}")
        else:
            print(f"ERROR: Error executing command: {error}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # Close SSH connection
        ssh_client.close()
        print(f"INFO: Disconnected from {hostname}")

def isReachable(hostname, port=443, timeout=5):
    try:
        with socket.create_connection((hostname, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def countdown(seconds, increment):
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer = f'{mins:02d}:{secs:02d}'
        print(f"INFO: Time Remaining: {timer}", end='\r')
        time.sleep(increment)
        seconds -= increment
    print("INFO: Countdown complete.")

def downloadFile(url, local_path):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                file.write(response.content)
            print(f"INFO: File downloaded successfully to {local_path}")
        else:
            print(f"ERROR: Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")