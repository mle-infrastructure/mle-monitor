from .resource.detect import determine_resource
from typing import Union


class MLEResource(object):
    def __init__(self, resource_name: Union[str, None] = None):
        """MLE Resource Instance - Get Monitoring Data."""
        if resource_name is None:
            self.resource_name = determine_resource()
        else:
            self.resource_name = resource_name

    def monitor(self):
        """Get utilization data."""
        # Get resource dependent data
        if self.resource_name == "sge-cluster":
            from .resource.monitor_sge import get_sge_data

            user_data, host_data, util_data = get_sge_data()
        elif self.resource_name == "slurm-cluster":
            from .resource.monitor_slurm import get_slurm_data

            user_data, host_data, util_data = get_slurm_data()
        elif self.resource_name == "gcp-cloud":
            from .resoruce.monitor_gcp import get_gcp_data

            gcp_data = get_gcp_data()
            # TODO: Figure out how to do this smarter
            return gcp_data
        else:  # Local!
            from .resource.monitor_local import get_local_data

            user_data, host_data, util_data = get_local_data()
        return user_data, host_data, util_data, self.resource_name
