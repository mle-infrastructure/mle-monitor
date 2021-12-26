## [v0.0.2] - [Unreleased]

### Added

### Changed

### Fixed

## [v0.0.1] - [12/09/2021]

### Added

Basic API for `MLEProtocol`, `MLEResource` & `MLEDashboard`:

```python
from mle_monitor import MLEProtocol

# Load protocol database or create new one -> print summary
protocol_db = MLEProtocol("mle_protocol.db", verbose=False)
protocol_db.summary(tail=10, verbose=True)

# Draft data to store in protocol & add it to the protocol
meta_data = {
    "purpose": "Grid search",  # Purpose of experiment
    "project_name": "MNIST",  # Project name of experiment
    "experiment_type": "hyperparameter-search",  # Type of experiment
    "experiment_dir": "experiments/logs",  # Experiment directory
    "num_total_jobs": 10,  # Number of total jobs to run
    ...
}
new_experiment_id = protocol_db.add(meta_data)

# ... train your 10 (pseudo) networks/complete respective jobs
for i in range(10):
    protocol_db.update_progress_bar(new_experiment_id)

# Wrap up an experiment (store completion time, etc.)
protocol_db.complete(new_experiment_id)
```
