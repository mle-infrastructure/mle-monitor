from datetime import datetime
import subprocess as sp
import pandas as pd
import numpy as np
from typing import Union
from ..utils import natural_keys


class SlurmResource(object):
    def __init__(self, monitor_config: Union[dict, None]):
        self.resource_name = "slurm-cluster"
        self.monitor_config = monitor_config

    def monitor(self):
        """Helper to get all utilisation data for resource."""
        user_data, job_df = self.get_user_data()
        host_data = self.get_partition_data(job_df)
        node_data = self.get_node_data(job_df)
        util_data = self.get_util_data()
        return user_data, host_data, util_data, node_data

    def get_user_data(self):
        """Get jobs scheduled by Slurm cluster users."""
        user_data = {"user": [], "total": [], "run": [], "wait": [], "login": []}

        # Get squeue output in detailed form
        processes = sp.check_output(
            [
                "squeue",
                "-o",
                '"%.20P %.20u %.2t %.10M %.6D %C %m %N"',
                "-p",
                (",").join(self.monitor_config["partitions"]),
            ]
        )
        all_job_infos = processes.split(b"\n")[1:-1]
        all_job_infos = [j.decode() for j in all_job_infos]

        job_df = {
            "user": [],
            "partition": [],
            "status": [],
            "node": [],
            "run_time": [],
            "num_cores": [],
            "min_memory": [],
        }
        # Loop over jobs and extract relevant data into dataframe
        for job in all_job_infos:
            job_clean = job.split()[1:]
            job_df["user"].append(job_clean[1])
            job_df["partition"].append(job_clean[0])
            job_df["status"].append(job_clean[2])
            job_df["run_time"].append(job_clean[3])
            job_df["node"].append(job_clean[7][:-1])
            job_df["num_cores"].append(job_clean[5])
            job_df["min_memory"].append(job_clean[6])
        job_df = pd.DataFrame(job_df)

        # Loop over unique users and construct data to show
        unique_users = job_df.user.unique().tolist()
        for u_id in unique_users:
            sub_df = job_df.loc[job_df["user"] == u_id]
            user_data["user"].append(u_id)
            user_data["total"].append(sub_df.shape[0])
            sub_run = sub_df.loc[sub_df["status"] == "R"]
            user_data["run"].append(sub_run.shape[0])
            sub_wait = sub_df.loc[sub_df["status"] == "PD"]
            # "CG" is completing status
            user_data["wait"].append(sub_wait.shape[0])
            user_data["login"].append(0)

        # Sort users based on total jobs in decreasing order
        sort_ids = np.argsort(-np.array(user_data["total"]))
        user_data["user"] = [user_data["user"][i] for i in sort_ids]
        user_data["total"] = [user_data["total"][i] for i in sort_ids]
        user_data["run"] = [user_data["run"][i] for i in sort_ids]
        user_data["wait"] = [user_data["wait"][i] for i in sort_ids]
        user_data["login"] = [user_data["login"][i] for i in sort_ids]
        return user_data, job_df

    def get_partition_data(self, job_df: pd.DataFrame):
        """Get jobs running on different Slurm cluster partitions."""
        host_data = {"host_id": [], "total": [], "run": [], "login": []}

        unique_partitions = job_df.partition.unique().tolist()
        unique_partitions.sort(key=natural_keys)
        for h_id in unique_partitions:
            sub_df = job_df.loc[job_df["partition"] == h_id]
            host_data["host_id"].append(h_id)
            host_data["total"].append(sub_df.shape[0])
            sub_run = sub_df.loc[sub_df["status"] == "R"]
            host_data["run"].append(sub_run.shape[0])
            host_data["login"].append(0)
        return host_data

    def get_util_data(self):
        """Get memory and CPU utilisation for specific slurm partition."""
        # Get squeue output in detailed form
        processes = sp.check_output(["sinfo", "--Node", "-o", '"%.20P %N %c %O %m %e"'])
        all_node_infos = processes.split(b"\n")[1:-1]
        all_node_infos = [j.decode() for j in all_node_infos]

        total_cores, used_cores, total_mem, used_mem = 0, 0, 0, 0
        for n_info in all_node_infos:
            node_clean = n_info.split()[1:]
            try:
                # Cores in threads and memory in GB
                total_cores += int(node_clean[2])
                used_cores += float(node_clean[2]) * float(node_clean[3]) / 100
                total_mem += float(node_clean[4]) / 1000
                # Total memory - free memory
                used_mem += (
                    float(node_clean[4]) / 1000 - float(node_clean[5][:-1]) / 1000
                )
            except Exception:
                pass

        util_data = {
            "cores": total_cores,
            "cores_util": used_cores,
            "mem": total_mem,
            "mem_util": used_mem,
            "time_date": datetime.now().strftime("%m/%d/%y"),
            "time_hour": datetime.now().strftime("%H:%M:%S"),
        }
        return util_data

    def get_node_data(self, job_df: pd.DataFrame):
        """Get jobs running on different Slurm cluster nodes."""
        host_data = {"host_id": [], "total": [], "run": [], "login": []}

        unique_nodes = job_df.node.unique().tolist()
        unique_nodes.sort(key=natural_keys)
        for h_id in unique_nodes:
            sub_df = job_df.loc[job_df["node"] == h_id]
            host_data["host_id"].append(h_id)
            host_data["total"].append(sub_df.shape[0])
            sub_run = sub_df.loc[sub_df["status"] == "R"]
            host_data["run"].append(sub_run.shape[0])
            host_data["login"].append(0)
        return host_data


# squeue -p partition_name
# sacct -j job_id (get resource!)
