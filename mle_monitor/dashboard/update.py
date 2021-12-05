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
    make_cpu_util_plot,
    make_memory_util_plot,
    make_protocol_total_plot,
    make_protocol_daily_plot,
)


def update_dashboard(layout, resource_data, protocol_data, usage_data):
    """Helper function that fills dashboard with life!"""
    # Fill the left-main with life!
    if resource_data["resource_name"] in ["sge-cluster", "slurm-cluster"]:
        table_user = make_user_jobs_cluster(resource_data["user_data"])
        table_nodes = make_node_jobs_cluster(resource_data["host_data"])
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_row(table_user)
        grid.add_row(table_nodes)
        layout["left"].update(
            Panel(
                Align.center(grid),
                border_style="red",
                title="Jobs by User/Resource",
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
    layout["center"].update(
        Panel(
            make_protocol(protocol_data["protocol_table"]),
            border_style="bright_blue",
            title="Experiment Protocol Summary",
        )
    )

    # Fill the right-main with life!
    layout["r-box1"].update(
        Panel(
            make_total_experiments(protocol_data["total_data"]),
            border_style="yellow",
            title="Total Number of Experiment Runs",
        )
    )
    layout["r-box2"].update(
        Panel(
            make_last_experiment(protocol_data["last_data"]),
            border_style="yellow",
            title="Last Experiment Configuration",
        )
    )
    layout["r-box3"].update(
        Panel(
            make_est_completion(protocol_data["time_data"]),
            border_style="yellow",
            title="Experiment Completion Time",
        )
    )

    # Fill the footer with life!
    layout["f-box1"].update(
        Panel(
            make_cpu_util_plot(usage_data),
            title=(
                "CPU Utilization"
                f" - Total: {int(resource_data['util_data']['cores_util'])}/"
                f"{int(resource_data['util_data']['cores'])}T"
            ),
            border_style="red",
        ),
    )
    layout["f-box2"].update(
        Panel(
            make_memory_util_plot(usage_data),
            title=(
                "Memory Utilization"
                f" - Total: {int(resource_data['util_data']['mem_util'])}/"
                f"{int(resource_data['util_data']['mem'])}G"
            ),
            border_style="red",
        )
    )

    layout["f-box3"].update(
        Panel(
            make_protocol_total_plot(protocol_data["summary_data"]),
            title=("Protocol Timeline: Total Experiments"),
            border_style="yellow",
        ),
    )
    layout["f-box4"].update(
        Panel(
            make_protocol_daily_plot(protocol_data["summary_data"]),
            title=("Protocol Timeline: Experiments/Day"),
            border_style="yellow",
        )
    )
    return layout
