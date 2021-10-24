import platform
import re
from mle_toolbox import mle_config


def determine_resource() -> str:
    """Check if cluster (sge/slurm) is available."""
    hostname = platform.node()
    on_sge_cluster = any(
        re.match(line, hostname) for line in mle_config.sge.info.node_reg_exp
    )
    on_slurm_cluster = any(
        re.match(line, hostname) for line in mle_config.slurm.info.node_reg_exp
    )
    on_sge_head = hostname in mle_config.sge.info.head_names
    on_slurm_head = hostname in mle_config.slurm.info.head_names
    if on_sge_head or on_sge_cluster:
        return "sge-cluster"
    elif on_slurm_head or on_slurm_cluster:
        return "slurm-cluster"
    else:
        return hostname
