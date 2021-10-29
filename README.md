# Lightweight Cluster/Cloud VM Monitoring 📺
[![Pyversions](https://img.shields.io/pypi/pyversions/mle-monitor.svg?style=flat-square)](https://pypi.python.org/pypi/mle-monitor)
[![PyPI version](https://badge.fury.io/py/mle-monitor.svg)](https://badge.fury.io/py/mle-monitor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/mle-monitor/blob/main/examples/getting_started.ipynb)
<a href="https://github.com/RobertTLange/mle-monitor/blob/main/docs/logo_transparent.png?raw=true"><img src="https://github.com/RobertTLange/mle-monitor/blob/main/docs/logo_transparent.png?raw=true" width="200" align="right" /></a>

`mle-monitor` provides three core functionalities:

- **`MLEProtocol`**: A composable protocol database API for ML experiments.
- **`MLEResource`**: A tool for obtaining cluster usage statistics (Slurm & GridEngine).
- **`MLEDashboard`**: A dashboard visualizing both resource usage and experiment protocol.

## The `MLEProtocol` API 🎮

```python
from mle_monitor import MLEProtocol
```

- Talk about GCS synchronization

## The `MLEResource` API 🎮

```python
from mle_monitor import MLEResource
```

## The `MLEDashboard` API 🎮

```python
from mle_monitor import MLEDashboard
```

## Development & Milestones for Next Release

You can run the test suite via `python -m pytest -vv tests/`. If you find a bug or are missing your favourite feature, feel free to contact me [@RobertTLange](https://twitter.com/RobertTLange) or create an issue :hugs:. Here are some features I want to implement for the next release:

- [ ] `MLEProtocol`
  - Make modular (core + extra) data to protocol
  - Integrate GCS synchronization
  - Add verbosity option for rich console logging
- [ ] `MLEResource`
  - Move `get_xyz_data` into resource classes
  - Return standardized monitoring data
- [ ] `MLEDashboard`
  - Add snapshot function
  - Get dashboard even without protocol usage?!
- [ ] Add gcloud db pull/send to `MLEProtocol`
  - credentials path as option
  - `protocol_db.pull_gcs()`, `protocol_db.send_gcs()`
- [ ] Make `mle-monitor` independent of `mle-toolbox`
- [ ] Make `mle-toolbox` work by default without `mle-hyperopt` and `mle-monitor`
- [ ] Add test suite
  - [ ] Protocol (add, delete, store, etc.)
  - [ ] Resource (resource detection?)
  - [ ] Dashboard (data correctness?)
