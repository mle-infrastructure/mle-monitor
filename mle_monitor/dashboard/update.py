from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from .components import (
    make_user_jobs_cluster,
    make_node_jobs_cluster,
    make_device_panel_local,
    make_process_panel_local,
    make_protocol,
    make_total_experiments,
    make_last_experiment,
    make_est_completion,
    make_util_plot,
    make_protocol_total_plot,
    make_protocol_daily_plot,
)


def update_dashboard(layout, resource_data, protocol_data, usage_data):
    """Helper function that fills dashboard with life!"""
    # Fill the left-main with life!
    if resource_data["resource_name"] in ["sge-cluster", "slurm-cluster"]:
        table_user = make_user_jobs_cluster(resource_data["user_data"])
        queue_var = (
            "PARTITION"
            if resource_data["resource_name"] == "slurm-cluster"
            else "QUEUE"
        )
        table_host = make_node_jobs_cluster(resource_data["host_data"], queue_var)
        table_node = make_node_jobs_cluster(resource_data["node_data"], "NODE")
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_row(table_user)
        grid.add_row(table_host)
        grid.add_row(table_node)
        layout["left"].update(
            Panel(
                Align.center(grid),
                border_style="red",
                title="Jobs by User/Queue/Node",
            )
        )
    else:
        table_device = make_device_panel_local(resource_data["host_data"])
        table_process = make_process_panel_local(resource_data["user_data"])
        grid = Table.grid()
        grid.add_column()
        grid.add_row(table_device)
        grid.add_row(table_process)

        layout["left"].update(
            Panel(
                Align.center(grid),
                border_style="red",
                title="Local - Util by Device/Process",
            )
        )

    # Fill the center-main with life!
    layout["top-right-left"].update(
        Panel(
            make_protocol(protocol_data["protocol_table"]),
            border_style="bright_blue",
            title="Experiment Protocol Summary",
        )
    )

    # Fill the right-main with life!
    layout["top-right-right-1"].update(
        Panel(
            make_total_experiments(protocol_data["total_data"]),
            border_style="yellow",
            title="Total Number of Experiment Runs",
        )
    )
    layout["top-right-right-2"].update(
        Panel(
            make_last_experiment(protocol_data["last_data"]),
            border_style="yellow",
            title="Last Experiment Configuration",
        )
    )
    layout["top-right-right-3"].update(
        Panel(
            make_est_completion(protocol_data["time_data"]),
            border_style="yellow",
            title="Experiment Completion Time",
        )
    )

    # Fill the footer with life!
    layout["bottom-right-1"].update(
        Panel(
            make_util_plot(usage_data),
            title=(
                f"CPU: {int(resource_data['util_data']['cores_util'])}/"
                f"{int(resource_data['util_data']['cores'])}T"
                f" - Memory: {int(resource_data['util_data']['mem_util'])}/"
                f"{int(resource_data['util_data']['mem'])}G"
            ),
            border_style="yellow",
        ),
    )

    layout["bottom-right-2"].update(
        Panel(
            make_protocol_total_plot(protocol_data["summary_data"]),
            title=("Protocol Timeline: Total Experiments"),
            border_style="yellow",
        ),
    )

    layout["bottom-right-3"].update(
        Panel(
            make_protocol_daily_plot(protocol_data["summary_data"]),
            title=("Protocol Timeline: Experiments/Day"),
            border_style="yellow",
        )
    )
    return layout
