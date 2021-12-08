import time
from rich.live import Live
from rich.console import Console
from . import MLEProtocol, MLEResource
from .utils import Tracker
from .dashboard import layout_dashboard, update_dashboard


class MLEDashboard(object):
    def __init__(self, protocol: MLEProtocol, resource: MLEResource):
        """MLE Resource Dashboard - Rich-based terminal output."""
        self.protocol = protocol
        self.resource = resource
        self.tracker = Tracker()

    def snapshot(self):
        """Get single console output snapshot."""
        # Create the layout
        layout = layout_dashboard(
            self.resource,
            self.protocol.use_gcs_protocol_sync,
            self.protocol.protocol_fname,
        )
        # Retrieve the data
        resource_data = self.resource.monitor()
        protocol_data = self.protocol.monitor()
        usage_data = self.tracker.update(resource_data["util_data"])
        # Update the layout and print it
        layout = update_dashboard(layout, resource_data, protocol_data, usage_data)
        Console().print(layout)

    def live(self):
        """Run constant monitoring in while loop."""
        # Generate the dashboard layout and display first data
        layout = layout_dashboard(
            self.resource,
            self.protocol.use_gcs_protocol_sync,
            self.protocol.protocol_fname,
        )

        resource_data = self.resource.monitor()
        protocol_data = self.protocol.monitor()
        usage_data = self.tracker.update(resource_data["util_data"])
        layout = update_dashboard(layout, resource_data, protocol_data, usage_data)

        # Start timers for GCS pulling and reloading of local protocol db
        timer_gcs = time.time()
        timer_db = time.time()

        # Run the live updating of the dashboard
        with Live(console=Console(), screen=True, auto_refresh=True) as live:
            live.update(layout)
            while True:
                try:
                    resource_data = self.resource.monitor()
                    protocol_data = self.protocol.monitor()
                    usage_data = self.tracker.update(
                        resource_data["util_data"], protocol_data["summary_data"]
                    )
                    layout = update_dashboard(
                        layout, resource_data, protocol_data, usage_data
                    )

                    # Every 10 seconds reload local database file
                    if time.time() - timer_db > 2:
                        self.protocol.load(pull_gcs=False)
                        timer_db = time.time()

                    # Every 5 minutes pull the newest DB from GCS
                    if time.time() - timer_gcs > 300:
                        self.protocol.load()
                        timer_gcs = time.time()
                except Exception:
                    pass
