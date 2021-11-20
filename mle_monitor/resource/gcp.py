import time
import subprocess as sp
import pandas as pd
from typing import Union


class GCPResource(object):
    def __init__(self, monitor_config: Union[dict, None]):
        self.resource_name = "gcp-cloud"
        self.monitor_config = monitor_config

    def monitor(self):
        """Helper to get all utilisation data for resource."""
        return self.get_data()

    def get_data(self):
        """Helper to get all utilisation data for GCP resource."""
        while True:
            try:
                check_cmd = [
                    "gcloud",
                    "compute",
                    "instances",
                    "list",
                    "--verbosity",
                    "error",
                ]
                out = sp.check_output(check_cmd)
                break
            except sp.CalledProcessError:
                time.sleep(1)

        # Clean up and check if vm_name is in list of all jobs
        job_info = out.split(b"\n")[1:-1]
        df_gcp = {"experiment_type": [], "status": []}
        for i in range(len(job_info)):
            decoded_job_info = job_info[i].decode("utf-8").split()
            df_gcp["experiment_type"].append(decoded_job_info[2])
            df_gcp["status"].append(decoded_job_info[-1])
        df_gcp = pd.DataFrame(df_gcp)

        gcp_data = {"experiment_type": [], "run": [], "stop": [], "stage": []}
        for jt in df_gcp.experiment_type.unique():
            sub_df = df_gcp[df_gcp.experiment_type == jt]
            run = (sub_df["status"] == "RUNNING").sum()
            stop = (sub_df["status"] == "STOPPING").sum()
            stage = (sub_df["status"] == "STAGING").sum()
            gcp_data["experiment_type"].append(jt)
            gcp_data["run"].append(run)
            gcp_data["stop"].append(stop)
            gcp_data["stage"].append(stage)
        # Return list of different machine types and their status
        return gcp_data
