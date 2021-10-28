from mle_monitor import MLEProtocol

meta_data = {
    "purpose": "Test MLEProtocol",
    "project_name": "MNIST",
    "exec_resource": "local",
    "experiment_dir": "log_dir",
    "experiment_type": "hyperparameter-search",
    "config_fname": "tests/fixtures/base_config.json",
    "num_seeds": 5,
    "num_total_jobs": 10,
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
    e_id = protocol.add(meta_data, save=False)
    proto_data = protocol.get(e_id)
    for k, v in meta_data.items():
        assert proto_data[k] == v
    return


def test_update_protocol():
    # Change some entry of DB store and check it
    return


def test_monitor_protocol():
    # Check that all required keys are in collected data
    return
