import os
import numpy as np


class Tracker(object):
    def __init__(self, fname=".mle_tracker.npy"):
        """MLE Tracker for Resource Utilization & Running Experiments."""
        self.fname = os.path.join(os.path.expanduser("~"), fname)
        # Storage limit & reload previous stored data
        self.limit = 100000
        self.load()

    def update(self, util_data: dict, save: bool = True):
        # Add utilisation data to storage dictionaries
        self.times_date.append(util_data["time_date"])
        self.times_hour.append(util_data["time_hour"])
        self.mem_util.append(util_data["mem_util"] / util_data["mem"])
        self.cpu_util.append(util_data["cores_util"] / util_data["cores"])
        self.moving_window()
        self.save()
        return {
            "times_date": self.times_date,
            "times_hour": self.times_hour,
            "rel_mem_util": self.mem_util,
            "rel_cpu_util": self.cpu_util,
        }

    def moving_window(self):
        """Truncate/Limit memory to approx. last 27 hours."""
        self.times_date = self.times_date[: self.limit]
        self.times_hour = self.times_hour[: self.limit]
        self.mem_util = self.mem_util[: self.limit]
        self.cpu_util = self.cpu_util[: self.limit]

    def load(self):
        """Creates a hidden file storing usage time series data."""
        try:
            data = np.load(self.fname)
            self.mem_util = data[:, 0].astype(np.float).tolist()
            self.cpu_util = data[:, 1].astype(np.float).tolist()
            self.times_date = data[:, 2].tolist()
            self.times_hour = data[:, 3].tolist()
        except Exception:
            # Start storing utilisation history
            self.mem_util = []
            self.cpu_util = []
            self.times_date = []
            self.times_hour = []

    def save(self):
        """Save recent usage time series data."""
        stacked = np.stack(
            [self.mem_util, self.cpu_util, self.times_date, self.times_hour], axis=1
        )
        np.save(self.fname, stacked)
