from datetime import datetime
import subprocess as sp
from typing import Union
import numpy as np
import pandas as pd
from ..utils import natural_keys


class SGEResource(object):
    def __init__(self, monitor_config: Union[dict, None]):
        self.resource_name = "sge-cluster"
        self.monitor_config = monitor_config

    def monitor(self):
        """Helper to get all utilisation data for resource."""
        user_data, job_df = self.get_user_data()
        queue_data = self.get_queue_data(job_df)
        node_data = self.get_node_data(job_df)
        util_data = self.get_util_data()
        return user_data, queue_data, util_data, node_data

    def get_user_data(self):
        """Get jobs scheduled by Slurm cluster users.
        Return dictionary with `users`, `total`, `run`, `wait`, `login`.
        """
        user_data = {"user": [], "total": [], "run": [], "wait": [], "login": []}
        all_users = sp.check_output(["qconf", "-suserl"]).split(b"\n")[:-1]
        all_users = [u.decode() for u in all_users]
        user_cmd = [["-u", u] for u in all_users]
        user_cmd = [item for sublist in user_cmd for item in sublist]
        queue_cmd = [["-q", q] for q in self.monitor_config["queues"]]
        queue_cmd = [item for sublist in queue_cmd for item in sublist]

        # Check all users and queues in one go
        all_job_infos = sp.check_output(["qstat", *user_cmd, *queue_cmd]).split(b"\n")[
            2:-1
        ]

        job_df = {
            "user": [],
            "queue": [],
            "status": [],
            "node": [],
        }

        # Clean all jobs (qlogin, qsub, etc.) + get unique users/hosts
        for job in all_job_infos:
            job_clean = job.decode().split(" ")
            job_clean = list(filter(None, job_clean))
            host_ip = job_clean[7].split("@")
            job_df["user"].append(job_clean[3])
            if len(host_ip) > 1:
                job_df["queue"].append(host_ip[0])
                job_df["node"].append(host_ip[1][:-1])
            else:
                job_df["queue"].append(None)
                job_df["node"].append(None)

            if "QLOGIN" in job_clean and job_clean[4] == "r":
                job_df["status"].append("LOGIN")
            elif "QLOGIN" not in job_clean and job_clean[4] == "r":
                job_df["status"].append("R")
            else:
                job_df["status"].append("PD")
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
            user_data["wait"].append(sub_wait.shape[0])
            sub_login = sub_df.loc[sub_df["status"] == "LOGIN"]
            user_data["login"].append(sub_login.shape[0])

        # Sort users based on total jobs in decreasing order
        sort_ids = np.argsort(-np.array(user_data["total"]))
        user_data["user"] = [user_data["user"][i] for i in sort_ids]
        user_data["total"] = [user_data["total"][i] for i in sort_ids]
        user_data["run"] = [user_data["run"][i] for i in sort_ids]
        user_data["wait"] = [user_data["wait"][i] for i in sort_ids]
        user_data["login"] = [user_data["login"][i] for i in sort_ids]
        return user_data, job_df

    def get_queue_data(self, job_df: pd.DataFrame):
        """Get jobs running on different SGE queues."""
        host_data = {"host_id": [], "total": [], "run": [], "login": []}
        job_df = job_df[job_df.status != "PD"]
        unique_queues = job_df.queue.unique().tolist()
        unique_queues.sort(key=natural_keys)

        for h_id in unique_queues:
            sub_df = job_df.loc[job_df["queue"] == h_id]
            host_data["host_id"].append(h_id)
            host_data["total"].append(sub_df.shape[0])
            sub_run = sub_df.loc[sub_df["status"] == "R"]
            host_data["run"].append(sub_run.shape[0])
            sub_login = sub_df.loc[sub_df["status"] == "LOGIN"]
            host_data["login"].append(sub_login.shape[0])
        return host_data

    def get_util_data(self):
        """Get memory and CPU utilisation for specific SGE queue."""
        processes = sp.check_output(["qhost"])
        all_node_infos = processes.split(b"\n")[1:-1]
        all_node_infos = [j.decode() for j in all_node_infos]

        total_cores, used_cores, total_mem, used_mem = 0, 0, 0, 0
        for n_info in all_node_infos:
            node_clean = n_info.split()
            try:
                # Cores in threads and memory in GB
                total_cores += int(node_clean[2])
                used_cores += float(node_clean[2]) * float(node_clean[6])
                total_mem += float(node_clean[-4][:-1])
                # Total memory - free memory
                used_mem += float(node_clean[-2][:-1])
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
        """Get jobs running on different SGE cluster nodes."""
        host_data = {"host_id": [], "total": [], "run": [], "login": []}
        job_df = job_df[job_df.status != "PD"]
        unique_nodes = job_df.node.unique().tolist()
        unique_nodes.sort(key=natural_keys)

        for h_id in unique_nodes:
            sub_df = job_df.loc[job_df["node"] == h_id]
            host_data["host_id"].append(h_id)
            host_data["total"].append(sub_df.shape[0])
            sub_run = sub_df.loc[sub_df["status"] == "R"]
            host_data["run"].append(sub_run.shape[0])
            sub_login = sub_df.loc[sub_df["status"] == "LOGIN"]
            host_data["login"].append(sub_login.shape[0])
        return host_data
