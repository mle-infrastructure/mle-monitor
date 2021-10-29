from mle_monitor import MLEProtocol

meta_data = {
    "purpose": "Test MLEProtocol",
    "project_name": "MNIST",
    "exec_resource": "local",
    "experiment_dir": "log_dir",
    "experiment_type": "hyperparameter-search",
    "base_fname": "main.py",
    "config_fname": "tests/fixtures/base_config.json",
    "num_seeds": 5,
    "num_total_jobs": 10,
    "num_jobs_per_batch": 5,
    "num_job_batches": 2,
    "time_per_job": "00:05:00",  # days-hours-minutes
    "num_cpus": 2,
    "num_gpus": 1,
}


def test_add_protocol():
    # Add experiment to new protocol and add data
    protocol = MLEProtocol(protocol_fname="mle_protocol.db")
    e_id = protocol.add(meta_data, save=False)
    proto_data = protocol.get(e_id)
    for k, v in meta_data.items():
        assert proto_data[k] == v
    return


def test_load_protocol():
    # Reload database - assert correctness of data
    protocol = MLEProtocol(protocol_fname="tests/fixtures/mle_protocol_test.db")
    last_data = protocol.get()
    for k, v in meta_data.items():
        if k not in ["config_fname", "purpose"]:
            assert last_data[k] == v

    # Check adding of new data
    e_id = protocol.add(meta_data, save=False)
    proto_data = protocol.get(e_id)
    for k, v in meta_data.items():
        assert proto_data[k] == v
    return


def test_update_delete_abort_protocol():
    # Change some entry of DB store and check it
    protocol = MLEProtocol(protocol_fname="mle_protocol.db")
    e_id = protocol.add(meta_data, save=False)
    # Update some element in the database
    protocol.update(e_id, "exec_resource", "slurm-cluster", save=False)
    assert protocol.get(e_id, "exec_resource") == "slurm-cluster"
    # Abort the experiment - changes status
    protocol.abort(e_id, save=False)
    assert protocol.status(e_id) == "aborted"
    return


def test_monitor_protocol():
    # Check that all required keys are in collected data
    protocol = MLEProtocol(protocol_fname="mle_protocol.db")
    e_id = protocol.add(meta_data, save=False)
    # Get the monitoring data - used later in dashboard
    total_data, last_data, time_data, protocol_table = protocol.monitor()
    total_keys = [
        "total",
        "run",
        "done",
        "aborted",
        "sge",
        "slurm",
        "gcp",
        "local",
        "report_gen",
        "gcs_stored",
        "retrieved",
    ]
    for k in total_keys:
        assert k in total_data.keys()
    last_keys = ["e_id", "e_dir", "e_type", "e_script", "e_config", "report_gen"]
    for k in last_keys:
        assert k in last_data.keys()
    time_keys = [
        "total_jobs",
        "total_batches",
        "jobs_per_batch",
        "time_per_batch",
        "start_time",
        "stop_time",
        "est_duration",
    ]
    for k in time_keys:
        assert k in time_data.keys()
    return
