# Import of helpers for protocoling experiments
import os
from mle_monitor import MLEProtocol


def run_protocol_gcs():
    """Protocol an experiment and sync it + results in GCS bucket."""
    # Define GCS settings - requires 'GOOGLE_APPLICATION_CREDENTIALS' env var.
    cloud_settings = {
        "project_name": "mle-toolbox",  # GCP project name
        "bucket_name": "mle-protocol",  # GCS bucket name
        "use_protocol_sync": True,  # Whether to sync the protocol to GCS
        "use_results_storage": True,  # Whether to sync experiment_dir to GCS
    }
    protocol_db = MLEProtocol("mle_protocol.db", cloud_settings, verbose=True)

    # Draft data to store in protocol
    meta_data = {
        "purpose": "Test 123",  # Purpose of experiment
        "project_name": "MNIST",  # Project name of experiment
        "exec_resource": "local",  # Resource jobs are run on
        "experiment_dir": "log_dir",  # Experiment log storage directory
        "experiment_type": "hyperparameter-search",  # Type of experiment to run
        "config_fname": "base_config.json",  # Config file path of experiment
    }
    new_experiment_id = protocol_db.add(meta_data)

    # ... train your network - or create a placeholder directory + file
    os.makedirs(meta_data["experiment_dir"])
    with open(os.path.join(meta_data["experiment_dir"], "readme.txt"), "w") as f:
        f.write("This is some example file for the mle-monitor example.")

    # Store experiment_dir as .zip in GCS bucket
    protocol_db.complete(new_experiment_id)


def retrieve_results():
    """Retrieve the stored experiment dir from GCS bucket and unzip it."""
    # Define GCS settings - requires 'GOOGLE_APPLICATION_CREDENTIALS' env var.
    cloud_settings = {
        "project_name": "mle-toolbox",  # GCP project name
        "bucket_name": "mle-protocol",  # GCS bucket name
        "use_protocol_sync": True,  # Whether to sync the protocol to GCS
        "use_results_storage": True,  # Whether to sync experiment_dir to GCS
    }
    protocol_db = MLEProtocol("mle_protocol.db", cloud_settings, verbose=True)

    # Retrieve last stored experiment from GCS bucket -> retrieved_log_dir
    protocol_db.retrieve(protocol_db.last_experiment_id, "retrieved_log_dir/")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Let's train a network.")
    parser.add_argument("-retrieve", "--retrieve", action="store_true", default=False)
    args = vars(parser.parse_args())
    if args["retrieve"]:
        retrieve_results()
    else:
        run_protocol_gcs()
