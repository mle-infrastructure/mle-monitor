from mle_hyperopt import RandomSearch
from mle_scheduler import MLEQueue
from mle_monitor import MLEProtocol
from mle_logging import load_meta_log


def main():
    """Full mle-infrastructure example: logging, search, queue, protocol."""
    # Load (existing) protocol database and add experiment data
    protocol_db = MLEProtocol("mle_protocol.db")
    meta_data = {
        "purpose": "random search",  # Purpose of experiment
        "project_name": "surrogate",  # Project name of experiment
        "exec_resource": "local",  # Resource jobs are run on
        "experiment_dir": "logs_search",  # Experiment log storage directory
        "experiment_type": "hyperparameter-search",  # Type of experiment to run
        "base_fname": "train.py",  # Main code script to execute
        "config_fname": "base_config.json",  # Config file path of experiment
        "num_seeds": 2,  # Number of evaluations seeds
        "num_total_jobs": 4,  # Number of total jobs to run
        "num_jobs_per_batch": 4,  # Number of jobs in single batch
        "num_job_batches": 1,  # Number of sequential job batches
        "time_per_job": "00:00:02",  # Expected duration: days-hours-minutes
    }
    new_experiment_id = protocol_db.add(meta_data)

    # Instantiate random search class
    strategy = RandomSearch(
        real={"lrate": {"begin": 0.1, "end": 0.5, "prior": "log-uniform"}},
        integer={"batch_size": {"begin": 1, "end": 5, "prior": "uniform"}},
        categorical={"arch": ["mlp", "cnn"]},
        verbose=True,
    )

    # Ask for configurations to evaluate & run parallel eval of seeds * configs
    configs, config_fnames = strategy.ask(2, store=True)
    queue = MLEQueue(
        resource_to_run="local",
        job_filename="train.py",
        config_filenames=config_fnames,
        random_seeds=[1, 2],
        experiment_dir="logs_search",
        protocol_db=protocol_db,
    )
    queue.run()

    # Merge logs of random seeds & configs -> load & get final scores
    queue.merge_configs(merge_seeds=True)
    meta_log = load_meta_log("logs_search/meta_log.hdf5")
    test_scores = [meta_log[r].stats.test_loss.mean[-1] for r in queue.mle_run_ids]

    # Update the hyperparameter search strategy
    strategy.tell(configs, test_scores)

    # Wrap up experiment (store completion time, etc.)
    protocol_db.complete(new_experiment_id)


if __name__ == "__main__":
    main()
