import platform
import cpuinfo
import socket
import uuid
import psutil
import re

def get_system_info():
    try:
        system_info = {
            "System": platform.uname().system,
            "Version": platform.uname().version,
            "Processor": cpuinfo.get_cpu_info()['brand_raw'],
            "IPAddress": socket.gethostbyname(socket.gethostname()),
            "MACAddress": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
        }
    except Exception as e:
        system_info = {key: "?" for key in ["System", "Version", "Processor", "IPAddress", "MACAddress"]}
    return system_info

def get_cpu_info():
    try:
        cpu_info = {
            "PhysicalCores": psutil.cpu_count(logical=False) or "?",
            "TotalCores": psutil.cpu_count(logical=True) or "?",
            "TotalCPUUsage": psutil.cpu_percent(interval=1, percpu=False) if psutil.WINDOWS else psutil.cpu_percent(interval=1),
        }
    except Exception as e:
        cpu_info = {key: "?" for key in ["PhysicalCores", "TotalCores", "TotalCPUUsage"]}
    return cpu_info

def get_memory_info():
    try:
        memory = psutil.virtual_memory()
        memory_info = {
            "TotalMemoryGB": f"{memory.total / (1024 ** 3):.2f}",
            "TotalAvailableGB": f"{memory.available / (1024 ** 3):.2f}",
            "TotalUsedGB": f"{memory.used / (1024 ** 3):.2f}",
        }
    except Exception as e:
        memory_info = {key: "?" for key in ["TotalMemoryGB", "TotalAvailableGB", "TotalUsedGB"]}
    return memory_info

def get_disk_info():
    disk_info = {}
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except Exception as e:
                print("Error while getting disk information for partition", partition.mountpoint, ":", e)
                continue

            partition_device = partition.device
            partition_usage_total = f"{partition_usage.total / (1024 ** 3):.2f}" 
            partition_usage_used = f"{partition_usage.used / (1024 ** 3):.2f}" 
            partition_usage_free = f"{partition_usage.free / (1024 ** 3):.2f}"

            disk_info[partition_device] = {
                "Total": partition_usage_total + " GB",
                "Used": partition_usage_used + " GB",
                "Free": partition_usage_free + " GB",
            }
    except Exception as e:
        pass
    return disk_info

# Get all the information using the defined functions
system_info = get_system_info()
cpu_info = get_cpu_info()
memory_info = get_memory_info()
disk_info = get_disk_info()

data_array = [system_info, cpu_info, memory_info, disk_info]

