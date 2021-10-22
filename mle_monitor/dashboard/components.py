from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.spinner import Spinner
from rich.ansi import AnsiDecoder

import datetime as dt
import numpy as np
import plotext as plt

from mle_toolbox import mle_config
from mle_toolbox.utils import determine_resource
from mle_toolbox.protocol import protocol_summary, generate_protocol_table


class Header:
    """Display header with clock and general toolbox configurations."""

    welcome_ascii = """            __  _____    ______   ______            ____
           /  |/  / /   / ____/  /_  __/___  ____  / / /_  ____  _  __
          / /|_/ / /   / __/______/ / / __ \/ __ \/ / __ \/ __ \| |/_/
         / /  / / /___/ /__/_____/ / / /_/ / /_/ / / /_/ / /_/ />  <
        /_/  /_/_____/_____/    /_/  \____/\____/_/_.___/\____/_/|_|
    """.splitlines()

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
            if mle_config.general.use_gcloud_protocol_sync
            else "\u2022 GCS Sync Protocol: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[1],
            "Author: @RobertTLange :bird:",
            # TODO: Figure out why link won't work if we use text != url
            # [u white link=https://twitter.com/RobertTLange]
        )
        resource = determine_resource()
        if resource == "sge-cluster":
            res = "sge"
        elif resource == "slurm-cluster":
            res = "slurm"
        elif resource == "gcp-cloud":
            res = "gcp"
        else:
            res = "local"

        if res in ["sge", "slurm", "gcp"]:
            user_on_resource = mle_config[res].credentials.user_name
        else:
            # Get local user name
            import getpass

            user_on_resource = getpass.getuser()

        grid.add_row(
            "\u2022 GCS Sync Results: [green]:heavy_check_mark:"
            if mle_config.general.use_gcloud_results_storage
            else "\u2022 GCS Sync Results: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[2],
            f"Resource: {resource}",
        )
        grid.add_row(
            f"\u2022 DB Path: {mle_config.general.local_protocol_fname}",
            Header.welcome_ascii[3],
            f"User: {user_on_resource}",
        )
        grid.add_row(
            f"\u2022 Env Name: {mle_config.general.remote_env_name}",
            Header.welcome_ascii[4],
            "Hi there! [not italic]:hugging_face:[/]",
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


def make_protocol() -> Table:
    """Generate rich table summarizing experiment protocol summary."""
    df = protocol_summary(tail=29, verbose=False)
    table = generate_protocol_table(df)
    return Align.center(table)


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

    if last_data["e_type"] == "hyperparameter-search":
        table.add_row(
            Text.from_markup("[b yellow]Search"),
            last_data["search_type"],
        )
        table.add_row(
            Text.from_markup("[b yellow]Metrics"),
            str(last_data["eval_metrics"]),
        )

        p_counter = 0
        for k in last_data["params_to_search"].keys():
            for var in last_data["params_to_search"][k].keys():
                if k == "categorical":
                    row = [var] + last_data["params_to_search"][k][var]
                elif k == "real":
                    try:
                        row = [
                            var,
                            last_data["params_to_search"][k][var]["begin"],
                            last_data["params_to_search"][k][var]["end"],
                            last_data["params_to_search"][k][var]["bins"],
                        ]
                    except Exception:
                        row = [
                            var,
                            last_data["params_to_search"][k][var]["begin"],
                            last_data["params_to_search"][k][var]["end"],
                            last_data["params_to_search"][k][var]["prior"],
                        ]
                elif k == "integer":
                    row = [
                        var,
                        last_data["params_to_search"][k][var]["begin"],
                        last_data["params_to_search"][k][var]["end"],
                        last_data["params_to_search"][k][var]["spacing"],
                    ]
                if p_counter == 0:
                    table.add_row(
                        Text.from_markup("[b yellow]Params"),
                        str(row),
                    )
                else:
                    table.add_row(
                        "",
                        str(row),
                    )
                p_counter += 1
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
        Text.from_markup("[b yellow]Est. Stop Time"), str(time_data["stop_time"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Est. Duration"), str(time_data["est_duration"])
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
    x = np.arange(len(cpu_hist["rel_cpu_util"]))
    y = np.array(cpu_hist["rel_cpu_util"])

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, line_marker=0, line_color="tomato", label="% CPU Util.")
    plt.figsize(42, 8)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(cpu_hist["times_hour"]) - 1]
    xlabels = [
        cpu_hist["times_date"][i][:5] + "-" + cpu_hist["times_hour"][i] for i in xticks
    ]
    plt.ticks(0, 3)
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
    x = np.arange(len(mem_hist["rel_mem_util"]))
    y = np.array(mem_hist["rel_mem_util"])

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, line_marker=0, line_color="tomato", label="% Memory Util.")
    plt.figsize(42, 8)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(mem_hist["times_hour"]) - 1]
    xlabels = [
        mem_hist["times_date"][i][:5] + "-" + mem_hist["times_hour"][i] for i in xticks
    ]
    plt.ticks(0, 3)
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
    from plotext.plot import (
        _size_max,
        _height_min,
        _height,
        _ylim_data,
        _ylim_plot,
        _yticks,
        _width_min,
        _width,
        _xlim_data,
        _xlim_plot,
        _xticks,
        _matrix,
        _grid,
        _add_data,
        _legend,
        _yaxis,
        _xaxis,
        _title,
        _axes_label,
        _canvas,
    )

    _size_max()
    _height_min()
    _height()
    _ylim_data()
    _ylim_plot()
    _yticks()
    _width_min()
    _width()
    _xlim_data()
    _xlim_plot()
    _xticks()
    _matrix()
    _grid()
    _add_data()
    _legend()
    _yaxis()
    _xaxis()
    _title()
    _axes_label()
    _canvas()
    return plt.par.canvas
