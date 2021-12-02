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
        }
        time_data = {
            "total_jobs": "-",
            "total_batches": "-",
            "jobs_per_batch": "-",
            "time_per_batch": "-",
            "start_time": "-",
            "stop_time": "-",
            "est_duration": "-",
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
    results = {
        "job_status": db.get(last_experiment_id, "job_status"),
        "total_jobs": db.get(last_experiment_id, "num_total_jobs"),
        "total_batches": db.get(last_experiment_id, "num_job_batches"),
        "jobs_per_batch": db.get(last_experiment_id, "num_jobs_per_batch"),
        "time_per_batch": db.get(last_experiment_id, "time_per_job"),
        "start_time": db.get(last_experiment_id, "start_time"),
        "stop_time": db.get(last_experiment_id, "stop_time"),
        "est_duration": db.get(last_experiment_id, "duration"),
    }
    return results


def get_last_experiment(db, last_experiment_id):
    """Get data from db to show in 'last_experiments' panel."""
    results = {
        "e_id": str(last_experiment_id),
        "e_dir": db.get(last_experiment_id, "experiment_dir"),
        "e_type": db.get(last_experiment_id, "experiment_type"),
        "e_script": db.get(last_experiment_id, "base_fname"),
        "e_config": db.get(last_experiment_id, "config_fname"),
        "report_gen": db.get(last_experiment_id, "report_generated"),
    }
    return results
