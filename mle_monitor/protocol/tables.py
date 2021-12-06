import pandas as pd
from datetime import datetime

from rich import box
from rich.table import Table
from rich.spinner import Spinner
from rich.console import Console
from rich.align import Align
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)


def protocol_summary(
    db, all_experiment_ids, tail: int = 5, verbose: bool = True, full: bool = False
):
    """Construct a summary dataframe of previous experiments."""
    # Set pandas df format option to print
    pd.set_option("display.max_columns", 5)
    pd.set_option("max_colwidth", 30)
    if len(all_experiment_ids) > 0:
        purposes, project_names, exp_paths = [], [], []
        num_seeds, statuses, start_times, experiment_types = [], [], [], []
        resource, num_cpus, num_gpus, total_jobs, completed_jobs = [], [], [], [], []
        if tail is None:
            tail = len(all_experiment_ids)

        # Loop over experiment ids and extract data to retrieve
        for int_e_id in all_experiment_ids[-tail:]:
            e_id = str(int_e_id)
            purposes.append(db.dget(e_id, "purpose"))
            project_names.append(db.dget(e_id, "project_name"))
            exp_paths.append(db.dget(e_id, "experiment_dir"))
            statuses.append(db.dget(e_id, "job_status"))
            start_times.append(db.dget(e_id, "start_time"))
            resource.append(db.dget(e_id, "exec_resource"))
            num_seeds.append(db.dget(e_id, "num_seeds"))
            num_cpus.append(db.dget(e_id, "num_cpus"))
            num_gpus.append(db.dget(e_id, "num_gpus"))
            experiment_types.append(db.dget(e_id, "experiment_type"))
            total_jobs.append(db.dget(e_id, "num_total_jobs"))
            completed_jobs.append(db.dget(e_id, "completed_jobs"))

        d = {
            "ID": [str(e_id) for e_id in all_experiment_ids[-tail:]],
            "Date": start_times,
            "Project": project_names,
            "Purpose": purposes,
            "Experiment Dir": exp_paths,
            "Status": statuses,
            "Seeds": num_seeds,
            "Resource": resource,
            "CPUs": num_cpus,
            "GPUs": num_gpus,
            "Type": experiment_types,
            "Jobs": total_jobs,
            "Completed Jobs": completed_jobs,
        }
        df = pd.DataFrame(d)
        df["Date"] = df["Date"].map("{:.5}".format)
        df["Purpose"] = df["Purpose"].map("{:.30}".format)

        # Print a nice table overview (no job resources)
        if verbose:
            Console().print(Align.left(protocol_table(df, full)))
        return df
    else:
        if verbose:
            time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
            print(time_t, "No previously recorded experiments")
        return None


def get_progress_bar(total_jobs: int, completed_jobs: int):
    progress = Progress(
        TextColumn(
            "{task.completed:^3.0f}/{task.total:^3.0f}", justify="left", style="white"
        ),
        BarColumn(bar_width=10, style="red"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style="white"),
        auto_refresh=False,
    )

    task = progress.add_task("queue", total=total_jobs)
    progress.update(task, completed=completed_jobs, refresh=True)
    return progress


def protocol_table(df, full: bool = True):
    """Generate pretty table of experiment protocol db - preselected db."""
    table = Table(show_header=True, show_footer=False, header_style="bold blue")
    table.add_column(":bookmark:", justify="center")
    table.add_column(":id:", justify="center")
    table.add_column(":spiral_calendar:", justify="center")
    table.add_column("Project")
    table.add_column("Purpose")
    table.add_column("Type")
    table.add_column("[yellow]:arrow_forward:", justify="center")
    table.add_column("[yellow]:recycle:", justify="center")
    table.add_column("CPU", justify="center")
    table.add_column("GPU", justify="center")
    # Full option prints also resource requirements of jobs
    if full:
        table.add_column(
            ":hourglass_flowing_sand: Completed Jobs [yellow]:heavy_check_mark:",
            justify="center",
        )

    # Add rows of info if dataframe exists (previously recorded experiments)
    if df is not None:
        for index in reversed(df.index):
            row = df.iloc[index]
            if row["Resource"] == "sge-cluster":
                resource = "SGE"
            elif row["Resource"] == "slurm-cluster":
                resource = "Slurm"
            elif row["Resource"] == "gcp-cloud":
                resource = "GCP"
            else:
                resource = "Local"

            if row["Type"] == "hyperparameter-search":
                exp_type = "search"
            elif row["Type"] == "multiple-configs":
                exp_type = "config"
            elif row["Type"] == "single-config":
                exp_type = "single"
            else:
                exp_type = row["Type"]

            if row["Status"] == "running":
                status = Spinner("dots", style="magenta")
            elif row["Status"] == "completed":
                status = "[green]:heavy_check_mark:"
            else:
                status = "[red]:heavy_multiplication_x:"

            if full:
                bar = get_progress_bar(int(row["Jobs"]), int(row["Completed Jobs"]))
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:10],
                    row["Purpose"][:15],
                    exp_type,
                    resource,
                    str(row["Seeds"]),
                    str(row["CPUs"]),
                    str(row["GPUs"]),
                    bar,
                )
            else:
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:10],
                    row["Purpose"][:25],
                    exp_type,
                    resource,
                    str(row["Seeds"]),
                    str(row["CPUs"]),
                    str(row["GPUs"]),
                )

    table.border_style = "blue"
    table.box = box.SIMPLE_HEAD
    return table
