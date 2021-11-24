# Import of helpers for protocoling experiments
import os
from mle_monitor import MLEProtocol


def main():
    # Define GCS settings for sync
    cloud_settings = {
        "project_name": "mle-toolbox",
        "bucket_name": "mle-protocol",
        "use_protocol_sync": True,
        "use_results_storage": True,
    }
    protocol_db = MLEProtocol("mle_protocol.db", cloud_settings, verbose=True)
    protocol_db.summary(tail=10, verbose=True)

    # Ask whether to abort/delete experiment data!
    if len(protocol_db) > 0:
        protocol_db.ask_for_e_id(action="delete")
        protocol_db.ask_for_e_id(action="abort")

    # Draft data to store in protocol
    purpose = protocol_db.ask_for_purpose()
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

    # ... train your network - create a directory
    os.makedirs(meta_data["experiment_dir"])

    protocol_db.complete(new_experiment_id)


if __name__ == "__main__":
    main()
