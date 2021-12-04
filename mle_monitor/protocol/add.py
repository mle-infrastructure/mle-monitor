import os
import hashlib
import json
import datetime as dt
from datetime import datetime
from typing import Union, Tuple
from ..utils import load_json_config, load_yaml_config


def protocol_experiment(
    db, last_experiment_id, standard: dict, extra: Union[dict, None] = None
):
    """Add the new experiment to the protocol database."""
    # Create a new db experiment entry
    new_experiment_id = str(last_experiment_id + 1)
    db.dcreate(new_experiment_id)

    # Add all standard & extra data points to protocol
    for k, v in standard.items():
        db.dadd(new_experiment_id, (k, v))

    if extra is not None:
        for k, v in extra.items():
            db.dadd(new_experiment_id, (k, v))

    # Add the git latest commit hash
    try:
        import git

        g = git.Repo(search_parent_directories=True)
        git_hash = g.head.object.hexsha
    except Exception:
        git_hash = "no-git-repo"
    db.dadd(new_experiment_id, ("git_hash", git_hash))

    # Add the base config - load from given configuration file(s)
    if type(standard["config_fname"]) == str:
        all_config_paths = [standard["config_fname"]]
    elif type(standard["base_train_config"]) == list:
        all_config_paths = standard["config_fname"]
    else:
        all_config_paths = []

    loaded_configs = []
    for config_path in all_config_paths:
        fname, fext = os.path.splitext(config_path)
        if fext == ".json":
            base_config = load_json_config(config_path)
        elif fext == ".yaml":
            base_config = load_yaml_config(config_path)
        else:
            base_config = {}
        loaded_configs.append(base_config)

    db.dadd(new_experiment_id, ("loaded_config", loaded_configs))

    # Hash to store results by in GCS bucket (timestamp, config_fname)
    config_to_hash = {
        **{"time": datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")},
        **{"config_fname": standard["config_fname"]},
    }
    hash_object = hashlib.md5(json.dumps(config_to_hash).encode("ASCII"))
    experiment_hash = hash_object.hexdigest()

    # Set of booleans: previously retrieved, stored in GCS, report generated
    db.dadd(new_experiment_id, ("e-hash", experiment_hash))
    db.dadd(new_experiment_id, ("retrieved_results", False))
    db.dadd(new_experiment_id, ("stored_in_cloud", False))
    db.dadd(new_experiment_id, ("report_generated", False))

    # Set the job status to running & calculate time till completion
    db.dadd(new_experiment_id, ("job_status", "running"))
    start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    est_duration, stop_time = estimate_experiment_duration(
        start_time, standard["time_per_job"], standard["num_job_batches"]
    )
    db.dadd(new_experiment_id, ("start_time", start_time))
    db.dadd(new_experiment_id, ("duration", est_duration))
    db.dadd(new_experiment_id, ("stop_time", stop_time))
    return db, int(new_experiment_id)


def estimate_experiment_duration(
    start_time: str, time_per_batch: str, total_batches: int
) -> Tuple[str, str]:
    """Estimate total duration and completion time of experiment."""
    days, hours, minutes = time_per_batch.split(":")
    hours_add, tot_mins = divmod(total_batches * int(minutes), 60)
    days_add, tot_hours = divmod(total_batches * int(hours) + hours_add, 24)
    tot_days = total_batches * int(days) + days_add
    tot_days, tot_hours, tot_mins = (str(tot_days), str(tot_hours), str(tot_mins))
    if len(tot_days) < 2:
        tot_days = "0" + tot_days
    if len(tot_hours) < 2:
        tot_hours = "0" + tot_hours
    if len(tot_mins) < 2:
        tot_mins = "0" + tot_mins

    start_date = dt.datetime.strptime(start_time, "%m/%d/%Y %H:%M:%S")
    end_date = start_date + dt.timedelta(
        days=int(float(tot_days)),
        hours=int(float(tot_hours)),
        minutes=int(float(tot_mins)),
    )
    est_duration = tot_days + ":" + tot_hours + ":" + tot_mins
    stop_time = end_date.strftime("%m/%d/%Y %H:%M:%S")
    return est_duration, stop_time
