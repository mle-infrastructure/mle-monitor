from typing import Union
from .resource import SGEResource, SlurmResource, LocalResource, GCPResource


class MLEResource(object):
    def __init__(
        self, resource_name: str = "local", monitor_config: Union[dict, None] = None
    ):
        """MLE Resource Instance - Get Monitoring Data."""
        assert resource_name in ["local", "sge-cluster", "slurm-cluster", "gcp-cloud"]
        self.resource_name = resource_name
        self.monitor_config = monitor_config

        if self.resource_name == "sge-cluster":
            self.resource = SGEResource(self.monitor_config)
        elif self.resource_name == "slurm-cluster":
            self.resource = SlurmResource(self.monitor_config)
        elif self.resource_name == "gcp-cloud":
            self.resource = GCPResource(self.monitor_config)
        else:
            self.resource = LocalResource(self.monitor_config)

    def monitor(self):
        """Get utilization data."""
        # Get resource dependent data
        if self.resource_name == "local":
            user_data, host_data, util_data = self.resource.monitor()
            return {
                "resource_name": self.resource_name,
                "user_data": user_data,
                "host_data": host_data,
                "util_data": util_data,
            }
        elif self.resource_name in ["sge-cluster", "slurm-cluster"]:
            user_data, host_data, util_data, node_data = self.resource.monitor()
            return {
                "resource_name": self.resource_name,
                "user_data": user_data,
                "host_data": host_data,
                "util_data": util_data,
                "node_data": node_data,
            }
        else:
            gcp_data = self.resource.monitor()
            return gcp_data
