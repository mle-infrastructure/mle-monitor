from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.spinner import Spinner
from rich.ansi import AnsiDecoder
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)
import datetime as dt
import numpy as np
import plotext as plt


class Header:
    """Display header with clock and general toolbox configurations."""

    welcome_ascii = """                        __                                 _ __
             ____ ___  / /__        ____ ___  ____  ____  (_) /_____  _____
            / __ `__ \/ / _ \______/ __ `__ \/ __ \/ __ \/ / __/ __ \/ ___/
           / / / / / / /  __/_____/ / / / / / /_/ / / / / / /_/ /_/ / /
          /_/ /_/ /_/_/\___/     /_/ /_/ /_/\____/_/ /_/_/\__/\____/_/
""".splitlines()

    def __init__(self, resource: str, use_gcs_sync: bool, protocol_fname: str):
        self.resource = resource
        self.use_gcs_sync = use_gcs_sync
        self.protocol_fname = protocol_fname

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            "General Settings:",
            Header.welcome_ascii[0],
            dt.datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        grid.add_row(
            "\u2022 GCS Sync Protocol: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Protocol: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[1],
            "Author: @RobertTLange :bird:",
            # [u white link=https://twitter.com/RobertTLange]
        )

        grid.add_row(
            "\u2022 GCS Sync Results: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Results: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[2],
            f"Resource: {self.resource.resource_name}",
        )
        grid.add_row(
            f"\u2022 DB Path: {self.protocol_fname}",
            Header.welcome_ascii[3],
            "Hi there! [not italic]:hugging_face:[/]",
        )
        grid.add_row(
            "",
            Header.welcome_ascii[4],
            "",
        )
        return Panel(grid, style="white on blue")


def make_user_jobs_cluster(user_data) -> Align:
    """Generate rich table summarizing jobs scheduled by users."""
    all_active_users = min(len(user_data["total"]), 13)
    sum_all = str(sum(user_data["total"]))
    sum_running = str(sum(user_data["run"]))
    sum_login = str(sum(user_data["login"]))
    sum_wait = str(sum(user_data["wait"]))

    # Create table with structure with aggregated numbers
    table = Table(
        show_header=True,
        show_footer=True,
        header_style="bold red",
        row_styles=["none", "dim"],
        border_style="red",
        box=box.SIMPLE,
    )
    table.add_column(
        "USER",
        Text.from_markup("[b]Total", justify="right"),
        style="white",
        justify="left",
    )
    table.add_column("ALL", sum_all, justify="center")
    table.add_column("RUN", sum_running, justify="center")
    table.add_column("LOG", sum_login, justify="center")
    table.add_column("W", sum_wait, justify="center")

    # Add row for each individual user
    for u_id in range(all_active_users):
        table.add_row(
            user_data["user"][u_id],
            str(user_data["total"][u_id]),
            str(user_data["run"][u_id]),
            str(user_data["login"][u_id]),
            str(user_data["wait"][u_id]),
        )
    return Align.center(table)


def make_node_jobs_cluster(host_data) -> Align:
    """Generate rich table summarizing jobs running on different nodes."""
    all_nodes = len(host_data["total"])
    sum_all = str(sum(host_data["total"]))
    sum_running = str(sum(host_data["run"]))
    sum_login = str(sum(host_data["login"]))

    table = Table(
        show_header=True,
        show_footer=True,
        header_style="bold red",
        row_styles=["none", "dim"],
        border_style="red",
        box=box.SIMPLE,
    )
    table.add_column(
        "NODE/PART",
        Text.from_markup("[b]Total", justify="right"),
        style="white",
        justify="left",
    )
    table.add_column("ALL", sum_all, justify="center")
    table.add_column("RUN", sum_running, justify="center")
    table.add_column("LOGIN", sum_login, justify="center")

    # Add row for each individual cluster/queue/partition node
    for h_id in range(all_nodes):
        table.add_row(
            host_data["host_id"][h_id],
            str(host_data["total"][h_id]),
            str(host_data["run"][h_id]),
            str(host_data["login"][h_id]),
        )
    return Align.center(table)


def make_device_panel_local(device_data) -> Align:
    """Generate rich table summarizing jobs running on different nodes."""
    sum_all = str(round(sum(device_data["percent_util"]), 1))
    t1 = Table(
        show_header=True,
        show_footer=True,
        header_style="bold red",
        row_styles=["none", "dim"],
        border_style="red",
        box=box.SIMPLE,
    )
    t1.add_column(
        "CORE",
        Text.from_markup("[b]Total", justify="right"),
        style="white",
        justify="left",
    )
    t1.add_column("UTIL", sum_all, justify="center")
    t1.add_column("CORE", "---", justify="center")
    t1.add_column("UTIL", "---", justify="center")

    # Add row for each individual core
    num_cores = len(device_data["core_id"])
    for i in range(int(num_cores / 2)):
        t1.add_row(
            "C-" + str(device_data["core_id"][i]),
            str(device_data["percent_util"][i]),
            "C-" + str(device_data["core_id"][int(i + num_cores / 2 - 1)]),
            str(device_data["percent_util"][int(i + num_cores / 2 - 1)]),
        )

    t2 = Table(
        show_header=True,
        show_footer=False,
        box=box.SIMPLE,
        border_style="red",
        header_style="bold red",
    )
    t2.add_column("GPU", style="white", justify="left")
    t2.add_column("LOAD-%", justify="center")
    t2.add_column("MEM-%", justify="center")
    t2.add_column("MEM-GB", justify="center")

    for i in range(len(device_data["gpu_name"])):
        t2.add_row(
            str(device_data["gpu_name"][i]),
            str(device_data["gpu_load"][i]),
            str(device_data["gpu_mem_util"][i]),
            str(device_data["gpu_mem_total"][i]),
        )

    table = Table(box=box.SIMPLE_HEAD, show_header=False, show_footer=True)
    table.add_column()
    table.add_row(t1)
    table.add_row(t2)
    return Align.center(table)
    return Align.center(table)


def make_process_panel_local(proc_data) -> Align:
    """Generate rich table summarizing jobs running on different nodes."""
    num_procs = len(proc_data["pid"])
    t1 = Table(
        show_header=True,
        show_footer=True,
        header_style="bold red",
        border_style="red",
        box=box.SIMPLE,
    )
    t1.add_column("PID", "---", style="white", justify="left")
    t1.add_column("NAME", "---", justify="center")
    t1.add_column("CPU-%", str(round(proc_data["total_cpu_util"], 1)), justify="center")
    t1.add_column(
        "MEM-MB", str(round(proc_data["total_mem_util"], 1)), justify="center"
    )

    for i in range(int(num_procs / 2)):
        t1.add_row(
            str(proc_data["pid"][i]),
            str(proc_data["p_name"][i][:6]),
            str(round(proc_data["cpu_util"][i], 1)),
            str(round(proc_data["mem_util"][i], 1)),
        )

    t2 = Table(show_header=False, show_footer=True, box=box.SIMPLE, border_style="red")
    t2.add_column("PID", style="white", justify="left")
    t2.add_column("NAME", justify="center")
    t2.add_column("CPU-%", justify="center")
    t2.add_column("MEM-MB", justify="center")

    for i in range(int(num_procs / 2), num_procs):
        t2.add_row(
            str(proc_data["pid"][i]),
            str(proc_data["p_name"][i][:6]),
            str(round(proc_data["cpu_util"][i], 1)),
            str(round(proc_data["mem_util"][i], 1)),
        )

    table = Table(box=box.SIMPLE_HEAD, show_header=False, show_footer=True)
    table.add_column()
    table.add_row(t1)
    table.add_row(t2)
    return Align.center(table)


def make_protocol(protocol_table) -> Table:
    """Generate rich table summarizing experiment protocol summary."""
    return Align.center(protocol_table)


def make_total_experiments(total_data) -> Align:
    """Generate rich table summarizing all experiments in protocol db."""
    table = Table(
        show_header=False,
        show_footer=False,
        header_style="bold yellow",
        border_style="yellow",
        box=box.SIMPLE_HEAD,
    )
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_row(
        "[b yellow]Total",
        Spinner("dots", style="magenta"),
        "[green]:heavy_check_mark:",
        "[red]:heavy_multiplication_x:",
    )
    table.add_row(
        total_data["total"],
        total_data["run"],
        total_data["done"],
        total_data["aborted"],
    )
    table.add_row(
        Text.from_markup("[b yellow]SGE"),
        Text.from_markup("[b yellow]Slurm"),
        Text.from_markup("[b yellow]GCP"),
        Text.from_markup("[b yellow]Local"),
    )
    table.add_row(
        total_data["sge"], total_data["slurm"], total_data["gcp"], total_data["local"]
    )
    table.add_row(
        Text.from_markup("[b yellow]-"),
        Text.from_markup("[b yellow]Report"),
        Text.from_markup("[b yellow]GCS"),
        Text.from_markup("[b yellow]Sync"),
    )
    table.add_row(
        "-", total_data["report_gen"], total_data["gcs_stored"], total_data["retrieved"]
    )
    return Align.center(table)


def make_last_experiment(last_data) -> Align:
    """Generate rich table summarizing last scheduled experiment settings."""
    table = Table(
        show_header=False,
        show_footer=False,
        box=box.SIMPLE_HEAD,
        header_style="bold yellow",
        border_style="yellow",
    )
    table.add_column()
    table.add_column()
    table.add_row(
        Text.from_markup("[b yellow]E-ID"),
        last_data["e_id"],
    )
    table.add_row(
        Text.from_markup("[b yellow]Type"),
        last_data["e_type"],
    )
    table.add_row(
        Text.from_markup("[b yellow]Dir."),
        last_data["e_dir"],
    )
    table.add_row(
        Text.from_markup("[b yellow]Script"),
        last_data["e_script"],
    )
    table.add_row(
        Text.from_markup("[b yellow]Config"),
        last_data["e_config"],
    )

    if last_data["job_status"] == "running":
        table.add_row(
            Text.from_markup("[b yellow]Status"),
            "Running :running:",
        )
    elif last_data["job_status"] == "completed":
        table.add_row(
            Text.from_markup("[b yellow]Status"),
            "Completed [green]:heavy_check_mark:",
        )
    elif last_data["job_status"] == "aborted":
        table.add_row(
            Text.from_markup("[b yellow]Status"),
            "Aborted [red]:heavy_multiplication_x:",
        )

    progress = Progress(
        TextColumn("{task.completed}/{task.total}", justify="left", style="magenta"),
        BarColumn(bar_width=10, style="magenta"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        auto_refresh=False,
    )

    task = progress.add_task("queue", total=10)
    progress.update(task, completed=2, refresh=True)

    table.add_row(
        Text.from_markup("[b yellow]#Jobs [green]:heavy_check_mark:"),
        progress,
    )
    return Align.center(table)


def make_est_completion(time_data) -> Align:
    """Generate rich table summarizing estim. time of experim. completion."""
    table = Table(
        show_header=False,
        show_footer=False,
        box=box.SIMPLE_HEAD,
        header_style="bold yellow",
        border_style="yellow",
    )
    table.add_column()
    table.add_column()
    table.add_row(
        Text.from_markup("[b yellow]Configs/Seeds"),
        f"{int(time_data['total_jobs']/time_data['num_seeds'])}/{time_data['num_seeds']}",
    )
    table.add_row(
        Text.from_markup("[b yellow]Total Jobs"), str(time_data["total_jobs"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Total Batches"), str(time_data["total_batches"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Jobs/Batch"), str(time_data["jobs_per_batch"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Time/Batch"), str(time_data["time_per_batch"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Start Time"), str(time_data["start_time"])
    )
    table.add_row(
        Text.from_markup("[b yellow]~ Stop Time"), str(time_data["stop_time"])
    )
    table.add_row(
        Text.from_markup("[b yellow]~ Duration"), str(time_data["est_duration"])
    )
    return Align.center(table)


def make_help_commands() -> Align:
    """Generate rich table summarizing core toolbox subcommands."""
    table = Table(
        show_header=True,
        show_footer=False,
        border_style="white",
        header_style="bold magenta",
        box=box.SIMPLE_HEAD,
    )
    table.add_column("Command", style="white", justify="left")
    table.add_column(
        "Function",
    )
    table.add_row(
        "mle run",
        "[b red] Experiment w. config .yaml",
    )
    table.add_row(
        "mle retrieve",
        "[b red] Retrieve from cluster/GCS",
    )
    table.add_row(
        "mle report",
        "[b red] Generate results .md report",
    )
    table.add_row(
        "mle monitor",
        "[b red] Monitor resource usage",
    )
    table.add_row(
        "mle init",
        "[b red] Init creds/default setup",
    )
    return table


def make_gcp_util(gcp_data) -> Align:
    """Generate rich table summarizing running GCP VM machines."""
    table = Table(
        show_header=True,
        show_footer=False,
        border_style="white",
        header_style="bold magenta",
        box=box.SIMPLE_HEAD,
    )
    table.add_column("Machine", style="white", justify="left")
    table.add_column("Run", justify="center")
    table.add_column("Stage", justify="center")
    table.add_column("Stop", justify="center")
    for m_id in range(len(gcp_data["experiment_type"])):
        table.add_row(
            str(gcp_data["experiment_type"][m_id]),
            str(gcp_data["run"][m_id]),
            str(gcp_data["stage"][m_id]),
            str(gcp_data["stop"][m_id]),
        )
    return table


def make_cpu_util_plot(cpu_hist) -> Align:
    """Plot curve displaying a CPU usage times series for the cluster."""
    x = np.arange(len(cpu_hist["rel_cpu_util"])).tolist()
    y = np.array(cpu_hist["rel_cpu_util"]).tolist()

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, marker="dot", color="red", label="% CPU Util.")
    plt.figure.plot_size(40, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(cpu_hist["times_hour"]) - 1]
    xlabels = [
        cpu_hist["times_date"][i][:5] + "-" + cpu_hist["times_hour"][i] for i in xticks
    ]
    plt.xticks(xticks, xlabels)
    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def make_memory_util_plot(mem_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    x = np.arange(len(mem_hist["rel_mem_util"])).tolist()
    y = np.array(mem_hist["rel_mem_util"]).tolist()

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, marker="dot", color="red", label="% Memory Util.")
    plt.figure.plot_size(40, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(mem_hist["times_hour"]) - 1]
    xlabels = [
        mem_hist["times_date"][i][:5] + "-" + mem_hist["times_hour"][i] for i in xticks
    ]
    plt.xticks(xticks, xlabels)
    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def plotext_helper():
    """Helper fct. that generates ansi string  to plot."""
    plt.figure.build()
    return plt.figure.canvas
