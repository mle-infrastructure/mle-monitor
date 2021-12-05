def get_monitor_db_data(db):
    """Helper to get all data from pickledb database."""
    if len(db.experiment_ids) > 0:
        total_data = get_total_experiments(db, db.experiment_ids)
        last_data = get_last_experiment(db, db.experiment_ids[-1])
        time_data = get_time_experiment(db, db.experiment_ids[-1])
    else:
        total_data = {
            "total": "0",
            "run": "0",
            "done": "0",
            "aborted": "0",
            "sge": "0",
            "slurm": "0",
            "gcp": "0",
            "local": "0",
            "report_gen": "0",
            "gcs_stored": "0",
            "retrieved": "0",
        }
        last_data = {
            "e_id": "-",
            "e_dir": "-",
            "e_type": "-",
            "e_script": "-",
            "e_config": "-",
            "report_gen": "-",
            "job_status": "-",
            "resource": "-",
        }
        time_data = {
            "job_status": "-",
            "total_jobs": 1,
            "total_batches": 1,
            "completed_jobs": 0,
            "jobs_per_batch": "-",
            "time_per_batch": "-",
            "start_time": "-",
            "stop_time": "-",
            "duration": "-",
            "num_seeds": 1,
        }
    return total_data, last_data, time_data


def get_total_experiments(db, all_experiment_ids):
    """Get data from db to show in 'total_experiments' panel."""
    run, done, aborted, sge, slurm, gcp, local = 0, 0, 0, 0, 0, 0, 0
    report_gen, gcs_stored, retrieved = 0, 0, 0
    for e_id in all_experiment_ids:
        status = db.get(e_id, "job_status")
        # Job status
        run += status == "running"
        done += status == "completed"
        aborted += status not in ["running", "completed"]
        # Execution resource data
        resource = db.get(e_id, "exec_resource")
        sge += resource == "sge-cluster"
        slurm += resource == "slurm-cluster"
        gcp += resource == "gcp-cloud"
        local += resource not in ["sge-cluster", "slurm-cluster", "gcp-cloud"]
        # Additional data: Report generated, GCS stored, Results retrieved
        try:
            report_gen += db.get(e_id, "report_generated")
            gcs_stored += db.get(e_id, "stored_in_gcloud")
            retrieved += db.get(e_id, "retrieved_results")
        except Exception:
            pass
    # Return results dictionary
    results = {
        "total": str(len(all_experiment_ids)),
        "run": str(run),
        "done": str(done),
        "aborted": str(aborted),
        "sge": str(sge),
        "slurm": str(slurm),
        "gcp": str(gcp),
        "local": str(local),
        "report_gen": str(report_gen),
        "gcs_stored": str(gcs_stored),
        "retrieved": str(retrieved),
    }
    return results


def get_time_experiment(db, last_experiment_id):
    """Get data from db to show in 'time_experiment' panel."""
    last_experiment = db.get(last_experiment_id)
    results = {
        "num_seeds": last_experiment["num_seeds"],
        "total_jobs": last_experiment["num_total_jobs"],
        "completed_jobs": last_experiment["completed_jobs"],
        "total_batches": last_experiment["num_job_batches"],
        "jobs_per_batch": last_experiment["num_jobs_per_batch"],
        "time_per_batch": last_experiment["time_per_job"],
        "start_time": last_experiment["start_time"],
        "stop_time": last_experiment["stop_time"],
        "duration": last_experiment["duration"],
        "job_status": last_experiment["job_status"],
    }
    return results


def get_last_experiment(db, last_experiment_id):
    """Get data from db to show in 'last_experiments' panel."""
    last_experiment = db.get(last_experiment_id)
    results = {
        "e_id": str(last_experiment_id),
        "job_status": last_experiment["job_status"],
        "e_dir": last_experiment["experiment_dir"],
        "e_type": last_experiment["experiment_type"],
        "e_script": last_experiment["base_fname"],
        "e_config": last_experiment["config_fname"],
        "report_gen": last_experiment["report_generated"],
        "resource": last_experiment["exec_resource"],
    }
    return results
