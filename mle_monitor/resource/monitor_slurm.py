from datetime import datetime
import subprocess as sp
import pandas as pd
import numpy as np


def get_slurm_data():
    """Helper to get all utilisation data for slurm resource."""
    user_data, job_df = get_user_slurm_data()
    host_data = get_host_slurm_data(job_df)
    util_data = get_util_slurm_data()
    return user_data, host_data, util_data


def get_user_slurm_data():
    """Get jobs scheduled by Slurm cluster users."""
    user_data = {"user": [], "total": [], "run": [], "wait": [], "login": []}

    try:
        # Get squeue output in detailed form
        processes = sp.check_output(
            ["squeue", "-o", '"%.20P %.20u %.2t %.10M %.6D %C %m %N"']
        )
        all_job_infos = processes.split(b"\n")[1:-1]
        all_job_infos = [j.decode() for j in all_job_infos]
    except Exception:
        pass

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


def get_host_slurm_data(job_df):
    """Get jobs running on different Slurm cluster hosts."""
    host_data = {"host_id": [], "total": [], "run": [], "login": []}

    unique_partitions = job_df.partition.unique().tolist()
    for h_id in unique_partitions:
        sub_df = job_df.loc[job_df["partition"] == h_id]
        host_data["host_id"].append(h_id)
        host_data["total"].append(sub_df.shape[0])
        sub_run = sub_df.loc[sub_df["status"] == "R"]
        host_data["run"].append(sub_run.shape[0])
        host_data["login"].append(0)
    return host_data


def get_util_slurm_data():
    """Get memory and CPU utilisation for specific slurm partition."""
    try:
        # Get squeue output in detailed form
        processes = sp.check_output(["sinfo", "--Node", "-o", '"%.20P %N %c %O %m %e"'])
        all_node_infos = processes.split(b"\n")[1:-1]
        all_node_infos = [j.decode() for j in all_node_infos]
    except Exception:
        pass

    total_cores, used_cores, total_mem, used_mem = 0, 0, 0, 0
    for n_info in all_node_infos:
        node_clean = n_info.split()[1:]
        try:
            # Cores in threads and memory in GB
            total_cores += int(node_clean[2])
            used_cores += float(node_clean[2]) * float(node_clean[3]) / 100
            total_mem += float(node_clean[4]) / 1000
            # Total memory - free memory
            used_mem += float(node_clean[4]) / 1000 - float(node_clean[5][:-1]) / 1000
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


# squeue -p partition_name
# sacct -j job_id (get resource!)


if __name__ == "__main__":
    print(get_slurm_data())
