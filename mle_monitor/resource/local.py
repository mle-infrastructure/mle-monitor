from datetime import datetime
import numpy as np
import psutil
import GPUtil
from typing import Union


class LocalResource(object):
    def __init__(self, monitor_config: Union[dict, None]):
        self.resource_name = "local"
        self.monitor_config = monitor_config

    def monitor(self):
        """Helper to get all utilisation data for local resource."""
        proc_data = self.get_process_data()
        device_data = self.get_device_data()
        util_data = self.get_util_data()
        return proc_data, device_data, util_data

    def get_process_data(self):
        """Get process info running on local machine."""
        proc_data = {
            "pid": [],
            "p_name": [],
            "mem_util": [],
            "cpu_util": [],
            "cmdline": [],
            "total_cpu_util": psutil.cpu_count() * psutil.cpu_percent(),
            "total_mem_util": (psutil.virtual_memory()._asdict()["used"] / 1000000),
        }

        # Get top 5 most memory/cpu demanding processes on local machine
        mem_sort, cpu_sort = self.get_cpu_processes()

        for p in cpu_sort:
            proc_data["pid"].append(p["pid"])
            proc_data["p_name"].append(p["name"])
            proc_data["mem_util"].append(p["vms"])
            proc_data["cpu_util"].append(p["cpu_percent"])
            proc_data["cmdline"].append(p["cmdline"])

        for p in mem_sort:
            proc_data["pid"].append(p["pid"])
            proc_data["p_name"].append(p["name"])
            proc_data["mem_util"].append(p["vms"])
            proc_data["cpu_util"].append(p["cpu_percent"])
            proc_data["cmdline"].append(p["cmdline"])
        return proc_data

    def get_cpu_processes(self, top_k: int = 6):
        """Get list of process sorted by Memory (MB)/CPU Usage (CPU%)."""
        listOfProcObjects = []
        # Iterate over the list
        for proc in psutil.process_iter():
            try:
                # Fetch process details as dict
                pinfo = proc.as_dict(attrs=["pid", "name", "username", "cmdline"])
                pinfo["vms"] = proc.memory_info().vms / (1024 * 1024 * 1000)
                pinfo["cpu_percent"] = proc.cpu_percent()
                # Append dict to list
                listOfProcObjects.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Sort list of dict by key vms i.e. memory usage
        sorted_by_memory = sorted(
            listOfProcObjects, key=lambda procObj: procObj["vms"], reverse=True
        )
        sorted_by_cpu = sorted(
            listOfProcObjects, key=lambda procObj: procObj["cpu_percent"], reverse=True
        )
        return sorted_by_memory[:top_k], sorted_by_cpu[:top_k]

    def get_device_data(self):
        """Get utilization per core."""
        device_data = {
            "core_id": np.arange(1, psutil.cpu_count() + 1),
            "percent_util": [
                round(e, 1) for e in psutil.cpu_percent(interval=1, percpu=True)
            ],
            "cpu_count": psutil.cpu_count(logical=True),
            "logical_count": psutil.cpu_count(),
        }
        # Add GPU usage data via GPUtil
        for k, v in self.get_nvidia_gpu_data().items():
            device_data[k] = v
        return device_data

    def get_nvidia_gpu_data(self):
        """Helper function to get NVIDIA GPU utilisation."""
        gpus = GPUtil.getGPUs()
        gpu_data = {
            "gpu_id": [],
            "gpu_name": [],
            "gpu_load": [],
            "gpu_mem_util": [],
            "gpu_mem_total": [],
            "gpu_mem_used": [],
        }

        # Loop over experts and add data
        for gp in gpus:
            gpu_data["gpu_id"].append(gp.id),
            gpu_data["gpu_name"].append(gp.name)
            # Load and memory usage in %
            gpu_data["gpu_load"].append(round(gp.load * 100, 1))
            gpu_data["gpu_mem_util"].append(round(gp.memoryUtil * 100, 1))
            # Memory in GB
            gpu_data["gpu_mem_total"].append(round(gp.memoryTotal / 1000, 1))
            gpu_data["gpu_mem_used"].append(round(gp.memoryUsed / 1000, 1))
        return gpu_data

    def get_util_data(self):
        """Get memory and CPU utilisation for specific local machine."""
        num_cpus = psutil.cpu_count()
        total_mem = psutil.virtual_memory()._asdict()["total"] / 1000000000
        used_mem = psutil.virtual_memory()._asdict()["used"] / 1000000000
        util_data = {
            "cores": num_cpus,
            "cores_util": num_cpus * psutil.cpu_percent() / 100,
            "mem": total_mem,
            "mem_util": used_mem,
            "time_date": datetime.now().strftime("%m/%d/%y"),
            "time_hour": datetime.now().strftime("%H:%M:%S"),
        }
        return util_data
