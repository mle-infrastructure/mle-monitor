class MLETracker(object):
    def __init__(self):
        """MLE Tracker for Resource Utilization & Running Experiments."""
        # Start storing utilisation history
        self.mem_util = []
        self.cpu_util = []
        self.times_date = []
        self.times_hour = []
        # Storage limit
        self.limit = 100000

    def update(self, util_data: dict):
        # Add utilisation data to storage dictionaries
        self.times_date.append(util_data["time_date"])
        self.times_hour.append(util_data["time_hour"])
        self.mem_util.append(util_data["mem_util"] / util_data["mem"])
        self.cpu_util.append(util_data["cores_util"] / util_data["cores"])
        self.moving_window()
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
