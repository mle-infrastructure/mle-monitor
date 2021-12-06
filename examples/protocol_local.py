# Import of helpers for protocoling experiments
import time
from mle_monitor import MLEProtocol, MLEResource, MLEDashboard


def run_protocol_local():
    """Protocol an experiment and update the progress status."""
    # Load (existing) protocol database and print summary
    protocol_db = MLEProtocol("mle_protocol.db", verbose=False)
    protocol_db.summary(tail=10, verbose=True)

    # Ask whether to abort/delete experiment data - only if previously used!
    if len(protocol_db) > 0:
        protocol_db.ask_for_e_id(action="delete")
        protocol_db.ask_for_e_id(action="abort")

    # Ask for command line input -> purpose of the experiment
    purpose = protocol_db.ask_for_purpose()

    # Draft data to store in protocol & add it to the protocol
    meta_data = {
        "purpose": purpose,  # Purpose of experiment
        "project_name": "MNIST",  # Project name of experiment
        "exec_resource": "local",  # Resource jobs are run on
        "experiment_dir": "log_dir",  # Experiment log storage directory
        "experiment_type": "hyperparameter-search",  # Type of experiment to run
        "base_fname": "main.py",  # Main code script to execute
        "config_fname": "base_config.json",  # Config file path of experiment
        "num_seeds": 5,  # Number of evaluations seeds
        "num_total_jobs": 10,  # Number of total jobs to run
        "num_jobs_per_batch": 5,  # Number of jobs in single batch
        "num_job_batches": 2,  # Number of sequential job batches
        "time_per_job": "00:05:00",  # Expected duration: days-hours-minutes
        "num_cpus": 2,  # Number of CPUs used in job
        "num_gpus": 1,  # Number of GPUs used in job
    }
    new_experiment_id = protocol_db.add(meta_data)

    # ... train your 10 (pseudo) networks/complete respective jobs
    for i in range(10):
        protocol_db.update_progress_bar(new_experiment_id)
        time.sleep(3)

    # Wrap up experiment (store completion time, etc.)
    protocol_db.complete(new_experiment_id)


def launch_dashboard():
    """Launch a dashboard displaying protocol summary and resource status."""
    # Load the protocol & define a resource monitor instance (on local machine)
    protocol = MLEProtocol("mle_protocol.db")
    resource = MLEResource(resource_name="local", monitor_config={})
    # You can also monitor slurm or grid engine clusters
    # resource = MLEResource(
    #     resource_name="slurm-cluster",
    #     monitor_config={"partitions": ["partition-1", "partition-2"]},
    # )
    # resource = MLEResource(
    #     resource_name="sge-cluster",
    #     monitor_config={"queues": ["queue-1", "queue-2"]}
    # )
    dashboard = MLEDashboard(protocol, resource)

    # Run the dashboard in a while loop
    dashboard.live()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Let's train a network.")
    parser.add_argument("-dash", "--dashboard", action="store_true", default=False)
    args = vars(parser.parse_args())
    if args["dashboard"]:
        launch_dashboard()
    else:
        run_protocol_local()
