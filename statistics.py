import psutil
import GPUtil
import platform
from datetime import datetime

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def secs2hours(secs):
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)

def get_system_info():
    uname = platform.uname()

    return {
    "System": f"{uname.system}",
    "Node Name": f"{uname.node}",
    "Release": f"{uname.release}",
    "Version": f"{uname.version}",
    "Machine": f"{uname.machine}",
    "Processor": f"{uname.processor}",
    }

def get_boot_time():
    # Boot Time
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)

    return {"Boot Time": f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"}

def get_battery_info():
    # Battery Details
    data = {}
    battery_object = psutil.sensors_battery()

    data["Battery Percent"] = battery_object.percent
    data["Battery Time Left"] = secs2hours(battery_object.secsleft)
    data["Battery Plugged"] = battery_object.power_plugged

    return data

def get_cpu_info():
    # let's print CPU information
    data = {}

    # number of cores
    data["Physical cores:"] = psutil.cpu_count(logical=False)
    data["Total cores:"] = psutil.cpu_count(logical=True)

    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    data["Max Frequency"] = f"{cpufreq.max:.2f}Mhz"
    data["Min Frequency"] = f"{cpufreq.min:.2f}Mhz"
    data["Current Frequency"] = f"{cpufreq.current:.2f}Mhz"

    # CPU usage
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        data[f"Core {i}"] = f"{percentage}%"
    data[f"Total CPU Usage"] =  f"{psutil.cpu_percent()}%"

    return data

def get_memory_info():
    # Memory Information
    data = {}

    # get the memory details
    svmem = psutil.virtual_memory()
    data["Virtual Total"] = get_size(svmem.total)
    data["Virtual Available"] = get_size(svmem.available)
    data["Virtual Used"] = get_size(svmem.used)
    data["Virtual Percentage"] = f"{svmem.percent}%"

    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    data["Swap Total"] = get_size(swap.total)
    data["Swap Free"] = get_size(swap.free)
    data["Swap Used"] = get_size(swap.used)
    data["Swap Percentage"] = f"{swap.percent}%"

    return data

def get_disk_info():
    # Disk Information
    data = {}

    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        data[partition.device] = {}
        data[partition.device]["Mountpoint"] = partition.mountpoint
        data[partition.device]["File system type"] = partition.fstype
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        data["Total Size"] = get_size(partition_usage.total)
        data["Used"] = get_size(partition_usage.used)
        data["Free"] = get_size(partition_usage.free)
        data["Percentage"] = f"{partition_usage.percent}%"

    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    data["Total read"] = get_size(disk_io.read_bytes)
    data["Total write"] = get_size(disk_io.write_bytes)

    return data

def get_network_info():
    # Network information
    data = {}

    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            data[interface_name] = {}
            if str(address.family) == 'AddressFamily.AF_INET':
                data["IP Address"] = address.address
                data["Netmask"] = address.netmask
                data["Broadcast IP"] = address.broadcast
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                data["MAC Address"] = address.address
                data["Netmask"] = address.netmask
                data["Broadcast MAC"] = address.broadcast

    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    data["Total Bytes Sent"] = get_size(net_io.bytes_sent)
    data["Total Bytes Received"] = get_size(net_io.bytes_recv)

    return data

def get_gpu_info():
    data = {}

    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        gpu_memory_utilization = f"{gpu.memoryUtil}%"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid

        data[gpu_id] = {
        "id": gpu.id,
        "name": gpu.name,
        "load": f"{gpu.load*100}%",
        "free_memory": f"{gpu.memoryFree}MB",
        "used_memory": f"{gpu.memoryUsed}MB",
        "total_memory": f"{gpu.memoryTotal}MB",
        "memory_utilization": f"{gpu.memoryUtil}%",
        "temperature": f"{gpu.temperature} °C",
        "uuid": gpu.uuid
        }

    return data

def get_statistics(interval = 1):
    pass

def get_layout2_statistics():
    battery_data = get_battery_info()
    system_data = get_system_info()
    ram_data = get_memory_info()
    cpu_data = get_cpu_info()
    gpu_data = get_gpu_info()

    final_data = {}

    final_data["Battery Percent"] = battery_data["Battery Percent"]
    final_data["System Name"] = system_data["Node Name"]
    final_data["RAM Percent"] = ram_data["Virtual Percentage"].replace('%', '')
    final_data["CPU Percent"] = cpu_data["Total CPU Usage"].replace('%', '')
    final_data["GPU Percent"] = gpu_data[0]["memory_utilization"].replace('%', '')
    final_data["Temperature"] = gpu_data[0]["temperature"].replace(' °C', '')

    return final_data
