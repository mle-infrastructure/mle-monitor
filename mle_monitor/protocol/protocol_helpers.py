import re
import pickledb
import pandas as pd
from datetime import datetime
import sys
import select
from typing import Union, List

from rich.console import Console
from rich.align import Align

from mle_toolbox import mle_config
from ..protocol.protocol_table import generate_protocol_table


def load_local_protocol_db():
    """Load local database from config name & reconstruct experiment id."""
    # Attempt loading local protocol database - otherwise return clean one
    db = pickledb.load(mle_config.general.local_protocol_fname, False)
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


def protocol_summary(tail: int = 5, verbose: bool = True):
    """Construct a summary dataframe of previous experiments."""
    # Load in the DB
    db, all_experiment_ids, last_experiment_id = load_local_protocol_db()
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
            table = Align.left(generate_protocol_table(df, full=False))
            console.print(table)
        return df
    else:
        if verbose:
            print(time_t, "No previously recorded experiments")
        return None


def update_protocol_var(
    experiment_id: str,
    db_var_name: Union[List[str], str],
    db_var_value: Union[list, str, dict],
):
    """Update variable(s) stored in protocol db for an experiment."""
    # Load in the DB
    db, all_experiment_ids, last_experiment_id = load_local_protocol_db()
    # Update the variable(s) of the experiment
    if type(db_var_name) == list:
        for db_v_id in range(len(db_var_name)):
            db.dadd(experiment_id, (db_var_name[db_v_id], db_var_value[db_v_id]))
    else:
        db.dadd(experiment_id, (db_var_name, db_var_value))
    db.dump()
    return db


def manipulate_protocol_from_input(delete: bool = False, abort: bool = False):
    """Ask user if they want to delete previous experiment by id."""
    time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    if delete:
        q_str = "{} Want to delete experiment? - state its id: [e_id/N]"
    elif abort:
        q_str = "{} Want to set exp. status to aborted? - state its id: [e_id/N]"
    print(q_str.format(time_t), end=" ")
    sys.stdout.flush()
    # Loop over experiments to delete until "N" given or timeout after 60 secs
    while True:
        i, o, e = select.select([sys.stdin], [], [], 60)
        if i:
            e_id = sys.stdin.readline().strip()
            if e_id == "N":
                break
        else:
            break

        # Make sure e_id can access db via key
        if e_id[:5] != "e-id-":
            e_id = "e-id-" + e_id

        # Load in the experiment protocol DB
        db, all_experiment_ids, _ = load_local_protocol_db()
        # Delete the dictionary in DB corresponding to e-id
        try:
            if delete:
                db.drem(e_id)
            elif abort:
                db.dadd(e_id, ("job_status", "aborted"))
            db.dump()
            print(
                "{} Another one? - state the next id: [e_id/N]".format(time_t), end=" "
            )
        except Exception:
            print(
                "\n{} The e_id is not in the protocol db. "
                "Please try again: [e_id/N]".format(time_t),
                end=" ",
            )
        sys.stdout.flush()
