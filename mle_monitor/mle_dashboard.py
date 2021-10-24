import time
from rich.live import Live
from mle_monitor import MLEProtocol, MLEResource
from .dashboard import layout_mle_dashboard, update_mle_dashboard


class MLEDashboard(object):
    def __init__(self, protocol: MLEProtocol, resource: MLEResource):
        """MLE Resource Dashboard - Rich-based terminal output."""
        self.protocol = protocol
        self.resource = resource

        # Start storing utilisation history
        self.util_hist = {
            "rel_mem_util": [],
            "rel_cpu_util": [],
            "times_date": [],
            "times_hour": [],
        }

    def snap(self):
        """Get single console output snapshot."""

    def live(self):
        """Run constant monitoring in while loop."""
        # Generate the dashboard layout and display first data
        layout = layout_mle_dashboard(self.resource)
        resource_data = self.resource.monitor()
        protocol_data = self.protocol.monitor()
        layout, self.util_hist = update_mle_dashboard(
            layout, self.util_hist, resource_data, protocol_data
        )

        # Start timers for GCS pulling and reloading of local protocol db
        timer_gcs = time.time()
        timer_db = time.time()

        # Run the live updating of the dashboard
        with Live(layout, refresh_per_second=10, screen=True):
            while True:
                try:
                    resource_data = self.resource.monitor()
                    protocol_data = self.protocol.monitor()
                    layout, self.util_hist = update_mle_dashboard(
                        layout, self.util_hist, resource_data, protocol_data
                    )

                    # Every 10 seconds reload local database file
                    if time.time() - timer_db > 10:
                        self.protocol.load(pull_gcs=False)
                        timer_db = time.time()

                    # Every 10 minutes pull the newest DB from GCS
                    if time.time() - timer_gcs > 600:
                        self.protocol.load()
                        timer_gcs = time.time()

                    # Truncate/Limit memory to approx. last 27 hours
                    self.util_hist["times_date"] = self.util_hist["times_date"][:100000]
                    self.util_hist["times_hour"] = self.util_hist["times_hour"][:100000]
                    self.util_hist["rel_mem_util"] = self.util_hist["rel_mem_util"][
                        :100000
                    ]
                    self.util_hist["rel_cpu_util"] = self.util_hist["rel_cpu_util"][
                        :100000
                    ]

                    # Wait a second
                    time.sleep(1)
                except Exception:
                    pass
