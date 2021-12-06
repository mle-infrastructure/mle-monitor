from rich import box
from rich.align import Align
from rich.table import Table
from rich.text import Text


def make_user_jobs_cluster(user_data: dict) -> Align:
    """Generate rich table summarizing jobs scheduled by users."""
    all_active_users = min(len(user_data["total"]), 13)
    sum_all = str(sum(user_data["total"]))
    sum_running = str(sum(user_data["run"]))
    # sum_login = str(sum(user_data["login"]))
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
        Text.from_markup("[b]Sum", justify="right"),
        style="white",
        justify="left",
    )
    table.add_column("ALL", sum_all, justify="center")
    table.add_column(":running:", sum_running, justify="center")
    # table.add_column(":astronaut:", sum_login, justify="center")
    table.add_column(":pause_button:", sum_wait, justify="center")

    # Add row for each individual user
    for u_id in range(all_active_users):
        table.add_row(
            user_data["user"][u_id],
            str(user_data["total"][u_id]),
            str(user_data["run"][u_id]),
            # str(user_data["login"][u_id]),
            str(user_data["wait"][u_id]),
        )
    return table


def make_node_jobs_cluster(host_data: dict, col_title: str) -> Align:
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
        col_title,
        Text.from_markup("[b]Sum", justify="right"),
        style="white",
        justify="left",
    )
    table.add_column("ALL", sum_all, justify="center")
    table.add_column(":running:", sum_running, justify="center")
    table.add_column(":construction_worker:", sum_login, justify="center")

    # Add row for each individual cluster/queue/partition node
    for h_id in range(all_nodes):
        table.add_row(
            host_data["host_id"][h_id],
            str(host_data["total"][h_id]),
            str(host_data["run"][h_id]),
            str(host_data["login"][h_id]),
        )
    return table


def make_device_panel_local(device_data: dict) -> Align:
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
        ":computer:",
        Text.from_markup("[b]Sum", justify="right"),
        style="white",
        justify="left",
    )
    t1.add_column("%", sum_all, justify="center")
    t1.add_column(":computer:", "---", justify="center")
    t1.add_column("%", "---", justify="center")

    # Add row for each individual core
    num_cores = len(device_data["core_id"])
    for i in range(int(num_cores / 2)):
        t1.add_row(
            "C" + str(device_data["core_id"][i]),
            str(device_data["percent_util"][i]),
            "C" + str(device_data["core_id"][int(i + num_cores / 2 - 1)]),
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
    t2.add_column(":computer: %", justify="center")
    t2.add_column(":floppy_disk: %", justify="center")
    t2.add_column("GB", justify="center")

    for i in range(len(device_data["gpu_name"])):
        t2.add_row(
            str(device_data["gpu_name"][i]),
            str(device_data["gpu_load"][i]),
            str(device_data["gpu_mem_util"][i]),
            str(device_data["gpu_mem_total"][i]),
        )

    table = Table(box=box.SIMPLE_HEAD, show_header=False, show_footer=False)
    table.add_column()
    table.add_row(t1)
    table.add_row(t2)
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
    t1.add_column(
        ":computer: %", str(round(proc_data["total_cpu_util"], 1)), justify="center"
    )
    t1.add_column(
        ":floppy_disk:", str(round(proc_data["total_mem_util"], 1)), justify="center"
    )

    for i in range(int(num_procs / 2)):
        t1.add_row(
            str(proc_data["pid"][i]),
            str(proc_data["p_name"][i][:6]),
            str(round(proc_data["cpu_util"][i], 1)),
            str(round(proc_data["mem_util"][i], 1)),
        )

    for i in range(int(num_procs / 2), num_procs):
        t1.add_row(
            str(proc_data["pid"][i]),
            str(proc_data["p_name"][i][:6]),
            str(round(proc_data["cpu_util"][i], 1)),
            str(round(proc_data["mem_util"][i], 1)),
        )
    return t1


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
