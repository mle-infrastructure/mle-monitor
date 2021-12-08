# Lightweight Experiment & Resource Monitoring 📺
[![Pyversions](https://img.shields.io/pypi/pyversions/mle-monitor.svg?style=flat-square)](https://pypi.python.org/pypi/mle-monitor)
[![PyPI version](https://badge.fury.io/py/mle-monitor.svg)](https://badge.fury.io/py/mle-monitor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mle-infrastructure/mle-monitor/blob/main/examples/getting_started.ipynb)
[![codecov](https://codecov.io/gh/mle-infrastructure/mle-monitor/branch/main/graph/badge.svg?75FIYZG8BD)](https://codecov.io/gh/mle-infrastructure/mle-monitor)
<a href="https://github.com/mle-infrastructure/mle-monitor/blob/main/docs/logo_transparent.png?raw=true"><img src="https://github.com/mle-infrastructure/mle-monitor/blob/main/docs/logo_transparent.png?raw=true" width="200" align="right" /></a>

"Did I already run this experiment before? How many resources are currently available on my cluster?" If these are common questions you encounter during your daily life as a researcher, then `mle-monitor` is made for you. It provides a lightweight API for tracking your experiments using a pickle protocol database (e.g. for hyperparameter searches and/or multi-configuration/multi-seed runs). Furthermore, it comes with built-in resource monitoring on Slurm/Grid Engine clusters and local machines/servers.

<img src="https://github.com/mle-infrastructure/mle-monitor/blob/main/docs/monitor-promo-gif?raw=true" alt="drawing" width="900"/>

`mle-monitor` provides three core functionalities:

- **`MLEProtocol`**: A composable protocol database API for ML experiments.
- **`MLEResource`**: A tool for obtaining server/cluster usage statistics.
- **`MLEDashboard`**: A dashboard visualizing resource usage & experiment protocol.

<img src="https://github.com/mle-infrastructure/mle-monitor/blob/main/docs/mle_monitor_structure.png?raw=true" alt="drawing" width="900"/>

## The `MLEProtocol` API 🎮

```python
from mle_monitor import MLEProtocol

# Load the protocol from a local file (create new if it doesn't exist yet)
protocol = MLEProtocol(protocol_fname="mle_protocol.db")

# Add meta data of experiment
experiment_data = {"purpose": "Test Protocol",
                   "project_name": "MNIST",
                   "exec_resource": "local",
                   "experiment_dir": "log_dir",
                   "experiment_type": "hyperparameter-search"}

e_id = protocol.add(experiment_data, save=False)

# Retrieve experiment data from protocol
protocol.get(e_id)
```

Additionally you can synchronize the protocol with a Google Cloud Storage (GCS) bucket by providing `gcs_project_name`, `gcs_bucket_name`, `gcs_protocol_fname` & `gcs_credentials_path`.

## The `MLEResource` API 🎮

```python
from mle_monitor import MLEResource

# Instantiate local resource and get usage data
resource = MLEResource(resource_name="local")
user_data, host_data, util_data, resource_name = resource.monitor()
```

## The `MLEDashboard` API 🎮

```python
from mle_monitor import MLEDashboard

# Instantiate dashboard with protocol and resource
dashboard = MLEDashboard(protocol, resource)

# Get a static snapshot of the protocol & resource utilisation
dashboard.snapshot()

# Run monitoring in while loop - dashboard
dashboard.live()
```

## Installation ⏳

A PyPI installation is available via:

```
pip install mle-monitor
```

Alternatively, you can clone this repository and afterwards 'manually' install it:

```
git clone https://github.com/mle-infrastructure/mle-monitor.git
cd mle-monitor
pip install -e .
```

## Development & Milestones for Next Release

You can run the test suite via `python -m pytest -vv tests/`. If you find a bug or are missing your favourite feature, feel free to contact me [@RobertTLange](https://twitter.com/RobertTLange) or create an issue :hugs:. Here are some features I want to implement for the next release:

- [ ] `MLEResource`
  - Add GCP VMs
  - Add SSH servers
- [ ] `MLEDashboard`
  - Add snapshot function
