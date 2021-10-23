import re
import pickledb
import pandas as pd
from datetime import datetime

from rich import box
from rich.table import Table
from rich.spinner import Spinner
from rich.console import Console
from rich.align import Align


def load_protocol_db(protocol_fname):
    """Load local database from config name & reconstruct experiment id."""
    # Attempt loading local protocol database - otherwise return clean one
    db = pickledb.load(protocol_fname, False)
    # Get the most recent experiment id
    all_experiment_ids = list(db.getall())

    def natural_keys(text: str):
        """Helper function for sorting alpha-numeric strings."""

        def atoi(text):
            return int(text) if text.isdigit() else text

        return [atoi(c) for c in re.split(r"(\d+)", text)]

    # Sort experiment ids & get the last one
    if len(all_experiment_ids) > 0:
        all_experiment_ids.sort(key=natural_keys)
        last_experiment_id = int(all_experiment_ids[-1].split("-")[-1])
    else:
        last_experiment_id = 0
    return db, all_experiment_ids, last_experiment_id


def protocol_summary(db, all_experiment_ids, tail: int = 5, verbose: bool = True):
    """Construct a summary dataframe of previous experiments."""
    # Set pandas df format option to print
    pd.set_option("display.max_columns", 5)
    pd.set_option("max_colwidth", 30)
    time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    if len(all_experiment_ids) > 0:
        purposes, project_names, exp_paths = [], [], []
        num_seeds, statuses, start_times, experiment_types = [], [], [], []
        resource, num_cpus, num_gpus, total_jobs = [], [], [], []
        if tail is None:
            tail = len(all_experiment_ids)
        for e_id in all_experiment_ids[-tail:]:
            purposes.append(db.dget(e_id, "purpose"))
            project_names.append(db.dget(e_id, "project_name"))
            exp_paths.append(db.dget(e_id, "exp_retrieval_path"))
            statuses.append(db.dget(e_id, "job_status"))
            start_times.append(db.dget(e_id, "start_time"))
            resource.append(db.dget(e_id, "exec_resource"))
            try:
                num_seeds.append(db.dget(e_id, "num_seeds"))
            except Exception:
                num_seeds.append("-")
            job_args = db.dget(e_id, "single_job_args")
            num_cpus.append(job_args["num_logical_cores"])
            try:
                num_gpus.append(job_args["num_gpus"])
            except Exception:
                num_gpus.append(0)

            # Get job type data
            meta_args = db.dget(e_id, "meta_job_args")
            if meta_args["experiment_type"] == "hyperparameter-search":
                experiment_types.append("search")
            elif meta_args["experiment_type"] == "multiple-experiments":
                experiment_types.append("multi")
            else:
                experiment_types.append("other")

            # Get number of jobs in experiement
            job_spec_args = db.dget(e_id, "job_spec_args")
            if meta_args["experiment_type"] == "hyperparameter-search":
                search_resources = job_spec_args["search_resources"]
                try:
                    if job_spec_args["search_config"]["search_schedule"] == "sync":
                        total_jobs.append(
                            search_resources["num_search_batches"]
                            * search_resources["num_evals_per_batch"]
                            * search_resources["num_seeds_per_eval"]
                        )
                    else:
                        total_jobs.append(
                            search_resources["num_total_evals"]
                            * search_resources["num_seeds_per_eval"]
                        )
                except Exception:
                    total_jobs.append(
                        search_resources["num_search_batches"]
                        * search_resources["num_evals_per_batch"]
                        * search_resources["num_seeds_per_eval"]
                    )
            elif meta_args["experiment_type"] == "multiple-experiments":
                total_jobs.append(
                    len(job_spec_args["config_fnames"]) * job_spec_args["num_seeds"]
                )
            else:
                total_jobs.append(1)

        d = {
            "ID": all_experiment_ids[-tail:],
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
        }
        df = pd.DataFrame(d)
        df["ID"] = [e.split("-")[-1] for e in df["ID"]]
        df["Date"] = df["Date"].map("{:.5}".format)
        df["Purpose"] = df["Purpose"].map("{:.30}".format)

        # Print a nice table overview (no job resources)
        if verbose:
            console = Console()
            table = Align.left(protocol_table(df, full=False))
            console.print(table)
        return df
    else:
        if verbose:
            print(time_t, "No previously recorded experiments")
        return None


def protocol_table(df, full=True):
    """Generate pretty table of experiment protocol db - preselected db."""
    table = Table(show_header=True, show_footer=False, header_style="bold blue")
    sta_str = "[green]:heavy_check_mark:[/green]/[red]:heavy_multiplication_x:"
    table.add_column(sta_str, justify="center")
    table.add_column("E-ID")
    table.add_column("Date")
    table.add_column("Project")
    table.add_column("Purpose")
    table.add_column("Type")
    table.add_column("[yellow]:arrow_forward:", justify="center")

    # Full option prints also resource requirements of jobs
    if full:
        table.add_column("#Jobs", justify="center")
        table.add_column("#CPU", justify="center")
        table.add_column("#GPU", justify="center")
        table.add_column("[yellow]:recycle:", justify="center")

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

            if row["Status"] == "running":
                status = Spinner("dots", style="magenta")
            elif row["Status"] == "completed":
                status = "[green]:heavy_check_mark:"
            else:
                status = "[red]:heavy_multiplication_x:"

            if full:
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:20],
                    row["Purpose"][:25],
                    row["Type"],
                    resource,
                    str(row["Jobs"]),
                    str(row["CPUs"]),
                    str(row["GPUs"]),
                    str(row["Seeds"]),
                )
            else:
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:20],
                    row["Purpose"][:25],
                    row["Type"],
                    resource,
                )

    table.border_style = "blue"
    table.box = box.SIMPLE_HEAD
    return table
