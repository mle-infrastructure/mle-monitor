from rich.panel import Panel
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
    user_data, host_data, util_data = resource_data
    total_data, last_data, time_data, protocol_table = protocol_data

    # # Fill the left-main with life!
    # if resource_name in ["sge-cluster", "slurm-cluster"]:
    #     layout["l-box1"].update(
    #         Panel(
    #             make_user_jobs_cluster(user_data),
    #             border_style="red",
    #             title="Scheduled Jobs by User",
    #         )
    #     )
    #     layout["l-box2"].update(
    #         Panel(
    #             make_node_jobs_cluster(host_data),
    #             border_style="red",
    #             title="Running Jobs by Node/Partition",
    #         )
    #     )
    # else:
    #     layout["l-box1"].update(
    #         Panel(
    #             make_device_panel_local(host_data),
    #             border_style="red",
    #             title="Local - Utilization by Device",
    #         )
    #     )
    #     layout["l-box2"].update(
    #         Panel(
    #             make_process_panel_local(user_data),
    #             border_style="red",
    #             title="Local - Utilization by Process",
    #         )
    #     )
    #
    # Fill the center-main with life!
    layout["center"].update(
        Panel(
            make_protocol(protocol_table),
            border_style="bright_blue",
            title="Experiment Protocol Summary",
        )
    )

    # Fill the right-main with life!
    layout["r-box1"].update(
        Panel(
            make_total_experiments(total_data),
            border_style="yellow",
            title="Total Number of Experiment Runs",
        )
    )
    layout["r-box2"].update(
        Panel(
            make_last_experiment(last_data),
            border_style="yellow",
            title="Last Experiment Configuration",
        )
    )
    layout["r-box3"].update(
        Panel(
            make_est_completion(time_data),
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
                f" - Total: {int(util_data['cores_util'])}/"
                f"{int(util_data['cores'])}T"
            ),
            border_style="red",
        ),
    )
    layout["f-box2"].update(
        Panel(
            make_memory_util_plot(usage_data),
            title=(
                "Memory Utilization"
                f" - Total: {int(util_data['mem_util'])}/"
                f"{int(util_data['mem'])}G"
            ),
            border_style="red",
        )
    )

    layout["f-box3"].update(
        Panel(
            make_protocol_total_plot(usage_data),
            title=("Protocol Timeline: Total Experiments"),
            border_style="yellow",
        ),
    )
    layout["f-box4"].update(
        Panel(
            make_protocol_daily_plot(usage_data),
            title=("Protocol Timeline: Experiments/Day"),
            border_style="yellow",
        )
    )
    return layout
