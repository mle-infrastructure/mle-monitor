from rich import box
from rich.align import Align
from rich.table import Table
from rich.text import Text
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)


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
        ":running:",
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
    table.add_row(
        Text.from_markup("[b yellow]Resource"),
        last_data["resource"],
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
        Text.from_markup("[b yellow]Conf/Seeds"),
        f"{int(time_data['total_jobs']/time_data['num_seeds'])}/{time_data['num_seeds']}",
    )
    table.add_row(
        Text.from_markup("[b yellow]Total Jobs"), str(time_data["total_jobs"])
    )
    table.add_row(
        Text.from_markup("[b yellow]# Batches"), str(time_data["total_batches"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Jobs/Batch"), str(time_data["jobs_per_batch"])
    )
    table.add_row(
        Text.from_markup("[b yellow]Time/Batch"),
        str(time_data["time_per_batch"][1:]),
    )
    table.add_row(
        Text.from_markup("[b yellow]Start Time"), str(time_data["start_time"])
    )
    if time_data["job_status"] == "completed":
        table.add_row(
            Text.from_markup("[b yellow]Stop Time"), str(time_data["stop_time"])
        )
        table.add_row(
            Text.from_markup("[b yellow]Duration"),
            str(time_data["duration"]),
        )
    else:
        table.add_row(
            Text.from_markup("[b yellow]~ Stop Time"), str(time_data["stop_time"])
        )
        table.add_row(
            Text.from_markup("[b yellow]~ Duration"),
            str(time_data["duration"]),
        )
    progress = Progress(
        TextColumn("{task.completed}/{task.total}", justify="left", style="magenta"),
        BarColumn(bar_width=10, style="magenta"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        auto_refresh=False,
    )

    task = progress.add_task("queue", total=time_data["total_jobs"])
    progress.update(task, completed=time_data["completed_jobs"], refresh=True)
    table.add_row(
        "[b yellow]-----------",
        "[b yellow]-----------------",
    )
    table.add_row(
        Text.from_markup(
            ":hourglass_flowing_sand: [b yellow]Jobs [green]:heavy_check_mark:"
        ),
        progress,
    )
    return Align.center(table)
