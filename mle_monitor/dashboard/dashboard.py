from rich.layout import Layout
from rich.panel import Panel

from .components import (
    Header,
    make_user_jobs_cluster,
    make_node_jobs_cluster,
    make_device_panel_local,
    make_process_panel_local,
    make_protocol,
    make_total_experiments,
    make_last_experiment,
    make_est_completion,
    make_help_commands,
    make_gcp_util,
    make_cpu_util_plot,
    make_memory_util_plot,
)


"""
TODOs:
- Make cluster resource calls more efficient/robust -> Faster at startup
- Add data collection functions for local + gcp!
    - monitor_gcp.py
- Replace help subcommand overview with GCS Bucket info => Only if used!
    - Jobs running
    - Bucket GB storage info
    - Last time all experiments where synced
- Link Author @RobertTLange to twitter account
"""


def layout_mle_dashboard(resource) -> Layout:
    """Define the MLE-Toolbox `monitor` base dashboard layout."""
    layout = Layout(name="root")
    # Split in three vertical sections: Welcome, core info, help + util plots
    layout.split(
        Layout(name="header", size=7),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=10),
    )
    # Split center into 3 horizontal sections
    layout["main"].split(
        Layout(name="left", ratio=0.35),
        Layout(name="center", ratio=1),
        Layout(name="right", ratio=0.35),
        direction="horizontal",
    )
    # Split center left into user info and node info
    if resource == "sge-cluster":
        layout["left"].split(
            Layout(name="l-box1", size=10), Layout(name="l-box2", size=25)
        )
    elif resource == "slurm-cluster":
        layout["left"].split(
            Layout(name="l-box1", size=20), Layout(name="l-box2", size=15)
        )
    else:
        layout["left"].split(
            Layout(name="l-box1", size=17), Layout(name="l-box2", size=18)
        )
    # Split center right into total experiments, last experiments, ETA
    layout["right"].split(
        Layout(name="r-box1", ratio=0.3),
        Layout(name="r-box2", ratio=0.4),
        Layout(name="r-box3", ratio=0.35),
    )
    # Split bottom into toolbox command info and cluster util termplots
    layout["footer"].split(
        Layout(name="f-box1", ratio=0.5),
        Layout(name="f-box2", ratio=0.5),
        Layout(name="f-box3", ratio=0.45),
        Layout(name="f-box4", ratio=0.55),
        direction="horizontal",
    )

    # Fill the header with life!
    layout["header"].update(Header())
    return layout


def update_mle_dashboard(layout, util_hist, resource_data, protocol_data):
    """Helper function that fills dashboard with life!"""
    user_data, host_data, util_data, resource_name = resource_data
    total_data, last_data, time_data, protocol_table = protocol_data
    # Add utilisation data to storage dictionaries
    util_hist["times_date"].append(util_data["time_date"])
    util_hist["times_hour"].append(util_data["time_hour"])
    util_hist["total_mem"] = util_data["mem"]
    util_hist["rel_mem_util"].append(util_data["mem_util"] / util_data["mem"])
    util_hist["total_cpu"] = util_data["cores"]
    util_hist["rel_cpu_util"].append(util_data["cores_util"] / util_data["cores"])

    # Fill the left-main with life!
    if resource_name in ["sge-cluster", "slurm-cluster"]:
        layout["l-box1"].update(
            Panel(
                make_user_jobs_cluster(user_data),
                border_style="red",
                title="Scheduled Jobs by User",
            )
        )
        layout["l-box2"].update(
            Panel(
                make_node_jobs_cluster(host_data),
                border_style="red",
                title="Running Jobs by Node/Partition",
            )
        )
    else:
        layout["l-box1"].update(
            Panel(
                make_device_panel_local(user_data),
                border_style="red",
                title="Local - Utilization by Device",
            )
        )
        layout["l-box2"].update(
            Panel(
                make_process_panel_local(host_data),
                border_style="red",
                title="Local - Utilization by Process",
            )
        )

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
            title="Est. Experiment Completion Time",
        )
    )

    # Fill the footer with life!
    layout["f-box1"].update(
        Panel(
            make_cpu_util_plot(util_hist),
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
            make_memory_util_plot(util_hist),
            title=(
                "Memory Utilization"
                f" - Total: {int(util_data['mem_util'])}/"
                f"{int(util_data['mem'])}G"
            ),
            border_style="red",
        )
    )
    # layout["f-box3"].update(
    #     Panel(
    #         make_gcp_util(gcp_data), title=("Google Cloud Platform"), border_style="red"
    #     )
    # )
    layout["f-box4"].update(
        Panel(
            make_help_commands(),
            border_style="white",
            title="[b white]Core MLE-Toolbox CLI",
        )
    )
    return layout, util_hist
