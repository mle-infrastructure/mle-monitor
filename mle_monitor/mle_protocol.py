from typing import Union, List
from datetime import datetime
import sys
import select
import logging
from .protocol import (
    load_protocol_db,
    protocol_summary,
    protocol_experiment,
    protocol_table,
    get_monitor_db_data,
)
from .utils import setup_logger


class MLEProtocol(object):
    def __init__(
        self,
        protocol_fname: str,
        cloud_settings: Union[dict, None] = None,
        verbose: bool = False,
    ):
        """MLE Protocol DB Instance."""
        self.protocol_fname = protocol_fname
        self.cloud_settings = cloud_settings
        self.verbose = verbose
        if self.verbose:
            self.logger = setup_logger(logging.INFO)
        else:
            self.logger = setup_logger(logging.WARNING)

        # Setup GCS credentials/data
        if self.cloud_settings is not None:
            # Don't use sync if cloud_setting dict is empty DotMap
            if len(self.cloud_settings.keys()) > 0:
                assert self.cloud_settings["project_name"] is not None
                assert self.cloud_settings["bucket_name"] is not None
                self.use_gcs_protocol_sync = self.cloud_settings["use_protocol_sync"]
                self.use_gcs_protocol_storage = self.cloud_settings[
                    "use_results_storage"
                ]

                if "credentials_path" in self.cloud_settings:
                    # Set the path to the GCP credentials json file & pull recent db
                    from .protocol import set_gcp_credentials

                    set_gcp_credentials(cloud_settings["credentials_path"])

                if "protocol_fname" not in self.cloud_settings:
                    self.cloud_settings["protocol_fname"] = self.protocol_fname
            else:
                self.use_gcs_protocol_sync = False
                self.use_gcs_protocol_storage = False
        else:
            self.use_gcs_protocol_sync = False
            self.use_gcs_protocol_storage = False
        self.load()

    def load(self, pull_gcs: bool = True):
        """Load the protocol data from a local pickle file."""
        if self.use_gcs_protocol_sync:
            if pull_gcs:
                self.accessed_gcs = self.gcs_pull()
            else:
                self.accessed_gcs = False
        else:
            self.accessed_gcs = False
        self.db, self.experiment_ids, self.last_experiment_id = load_protocol_db(
            self.protocol_fname
        )

    def get(
        self,
        experiment_id: Union[str, int, None] = None,
        var_name: Union[str, None] = None,
    ):
        """Retrieve variable from database."""
        if experiment_id is None:
            experiment_id = str(self.last_experiment_id)
        elif type(experiment_id) == int:
            experiment_id = str(experiment_id)

        if var_name is None:
            return self.db.get(experiment_id)
        else:
            return self.db.dget(experiment_id, var_name)

    def save(self, send_gcs: bool = True):
        """Dump the protocol db to its pickle file."""
        self.db.dump()
        self.logger.info(f"Locally stored protocol: {self.protocol_fname}")

        # Send recent/up-to-date experiment DB to Google Cloud Storage
        if send_gcs and self.use_gcs_protocol_sync:
            if self.accessed_gcs:
                self.gcs_send()
                self.logger.info(f"GCS synced protocol: {self.protocol_fname}")

    @property
    def standard_keys(self):
        """All required keys in standard dict to supply in `add`."""
        return [
            "purpose",
            "project_name",
            "exec_resource",
            "experiment_dir",
            "experiment_type",
            "base_fname",
            "config_fname",
            "num_seeds",
            "num_total_jobs",
            "num_job_batches",
            "num_jobs_per_batch",
            "time_per_job",
            "num_cpus",
            "num_gpus",
        ]

    @property
    def standard_default(self):
        """All required keys in standard dict to supply in `add`."""
        return {
            "purpose": "None provided",
            "project_name": "default",
            "exec_resource": "local",
            "experiment_dir": "experiments",
            "experiment_type": "single",
            "base_fname": "main.py",
            "config_fname": "base_config.yaml",
            "num_seeds": 1,
            "num_total_jobs": 1,
            "num_job_batches": 1,
            "num_jobs_per_batch": 1,
            "time_per_job": "00:01:00",
            "num_cpus": 1,
            "num_gpus": 0,
        }

    def add(
        self,
        standard: dict,
        extra: Union[dict, None] = None,
        save: bool = True,
        send_gcs: bool = True,
    ):
        """Add an experiment to the database."""
        for k in self.standard_keys:
            if k not in standard.keys():
                standard[k] = self.standard_default[k]
        assert standard["experiment_type"] in [
            "hyperparameter-search",
            "multiple-configs",
            "single-config",
        ]
        self.db, new_experiment_id = protocol_experiment(
            self.db, self.last_experiment_id, standard, extra
        )
        self.experiment_ids.append(new_experiment_id)
        self.last_experiment_id = new_experiment_id
        self.added_experiment_id = new_experiment_id
        self.completed_jobs_counter = 0
        self.logger.info(f"Added experiment {new_experiment_id} to protocol.")
        if save:
            self.save(send_gcs)
        return new_experiment_id

    def abort(
        self, experiment_id: Union[int, str], save: bool = True, send_gcs: bool = True
    ):
        """Abort an experiment - change status in db."""
        self.db.dadd(str(experiment_id), ("job_status", "aborted"))
        if save:
            self.save(send_gcs)

    def delete(
        self, experiment_id: Union[int, str], save: bool = True, send_gcs: bool = True
    ):
        """Delete an experiment - change status in db."""
        self.db.drem(str(experiment_id))
        self.all_experiment_ids = list(self.db.getall())
        try:
            self.all_experiment_ids.remove("summary")
        except Exception:
            pass
        if len(self.all_experiment_ids) > 0:
            self.last_experiment_id = int(self.all_experiment_ids[-1])
        else:
            self.last_experiment_id = 0
        if save:
            self.save(send_gcs)

    def update_progress_bar(
        self,
        experiment_id: Union[int, str, None] = None,
        completed_increment: int = 1,
        pull_gcs: bool = False,
        save: bool = True,
        send_gcs: bool = False,
    ):
        """Update progress bar of completed jobs using an integer increment."""
        if experiment_id is None:
            experiment_id = self.added_experiment_id
        self.load(pull_gcs)
        self.completed_jobs_counter += completed_increment
        self.update(
            experiment_id,
            "completed_jobs",
            self.completed_jobs_counter,
            save=save,
            send_gcs=send_gcs,
        )

    def complete(
        self, experiment_id: Union[int, str], report: bool = False, save: bool = True
    ):
        """Set status of an experiment to completed - change status in db."""
        self.load()
        experiment_data = self.get(experiment_id)
        # Store experiment directory in GCS bucket under hash
        if self.use_gcs_protocol_storage:
            from .utils import send_gcloud_zip

            zip_to_store = experiment_data["e-hash"] + ".zip"
            experiment_dir = experiment_data["experiment_dir"]
            send_gcloud_zip(self.cloud_settings, experiment_dir, zip_to_store, True)
            self.logger.info(f"Send results to GCS: {zip_to_store}")

        # Update and send protocol db
        time_t = datetime.now().strftime("%m/%d/%y %H:%M")
        stop_time = datetime.strptime(time_t, "%m/%d/%y %H:%M")
        start_time = datetime.strptime(experiment_data["start_time"], "%m/%d/%y %H:%M")
        duration = str(stop_time - start_time)
        self.update(
            experiment_id,
            var_name=[
                "job_status",
                "stop_time",
                "duration",
                "report_generated",
                "stored_in_gcloud",
                "completed_jobs",
            ],
            var_value=[
                "completed",
                time_t,
                duration,
                report,
                self.use_gcs_protocol_storage,
                experiment_data["num_total_jobs"],
            ],
            save=save,
        )
        self.logger.info(f"Updated protocol - COMPLETED: {experiment_id}")

    def status(self, experiment_id: Union[int, str]) -> str:
        """Get the status of an experiment."""
        return self.db.dget(str(experiment_id), "job_status")

    def update(
        self,
        experiment_id: Union[int, str],
        var_name: Union[List[str], str],
        var_value: Union[list, str, dict],
        save: bool = True,
        send_gcs: bool = True,
    ):
        """Update the data of an experiment."""
        # Update the variable(s) of the experiment
        if type(var_name) == list:
            for db_v_id in range(len(var_name)):
                self.db.dadd(
                    str(experiment_id), (var_name[db_v_id], var_value[db_v_id])
                )
        else:
            self.db.dadd(str(experiment_id), (var_name, var_value))
        if save:
            self.save(send_gcs)

    def summary(
        self,
        tail: int = 5,
        verbose: bool = True,
        return_table: bool = False,
        full: bool = False,
    ):
        """Print a rich summary table of all experiments in db."""
        summary = protocol_summary(self.db, self.experiment_ids, tail, verbose, full)
        if return_table:
            return protocol_table(summary, full)
        return summary

    def monitor(self):
        """Get monitoring data used in dashboard."""
        total_data, last_data, time_data = get_monitor_db_data(self)
        protocol_table = self.summary(
            tail=50, verbose=False, return_table=True, full=True
        )
        summary_data = self.get("summary")
        if not summary_data:
            summary_data = {
                "time": [],
                "day": [],
                "total_exp": {
                    "all": [],
                    "hyperparameter-search": [],
                    "multiple-configs": [],
                    "single-config": [],
                },
                "day_exp": {
                    "all": [],
                    "hyperparameter-search": [],
                    "multiple-configs": [],
                    "single-config": [],
                },
            }
        return {
            "total_data": total_data,
            "last_data": last_data,
            "time_data": time_data,
            "summary_data": summary_data,
            "protocol_table": protocol_table,
        }

    def retrieve(
        self,
        experiment_id: Union[int, str],
        local_dir_name: Union[None, str] = None,
    ):
        """Retrieve experiment from GCS."""
        from .utils import get_gcloud_zip

        while True:
            if str(experiment_id) not in self.experiment_ids:
                time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
                print(
                    time_t, "The experiment you are trying to retrieve does not exist"
                )
                experiment_id = input(
                    time_t + " Which experiment do you want to retrieve?"
                )
            else:
                break

        # Update protocol retrieval status of the experiment
        hash_to_store = self.get(experiment_id, "e-hash")
        get_gcloud_zip(
            self.cloud_settings, hash_to_store, experiment_id, local_dir_name
        )
        self.update(experiment_id, "retrieved_results", True)

        self.logger.info(f"Retrieved results from GCS bucket: {experiment_id}.")

    def gcs_send(self):
        """Send the local protocol to a GCS bucket."""
        # First store the most recent log
        from .protocol import send_gcloud_db

        send_db = send_gcloud_db(
            self.cloud_settings["project_name"],
            self.cloud_settings["bucket_name"],
            self.cloud_settings["protocol_fname"],
            self.protocol_fname,
        )
        self.logger.info(
            f"Send protocol to GCS bucket: {self.cloud_settings['bucket_name']}."
        )
        return send_db

    def gcs_pull(self):
        """Pull the remote protocol from a GCS bucket."""
        from .protocol import get_gcloud_db

        accessed_db = get_gcloud_db(
            self.cloud_settings["project_name"],
            self.cloud_settings["bucket_name"],
            self.cloud_settings["protocol_fname"],
            self.protocol_fname,
        )
        self.logger.info(
            f"Pulled protocol from GCS bucket: {self.cloud_settings['bucket_name']}."
        )
        return accessed_db

    def __len__(self) -> int:
        """Return number of experiments stored in protocol."""
        return len(self.experiment_ids)

    def ask_for_e_id(self, action: str = "delete"):
        """Ask user if they want to delete/abort previous experiment by id."""
        time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        q_str = "{} Want to {} an experiment? - state its id: [e_id/N]"
        print(q_str.format(time_t, action), end=" ")
        sys.stdout.flush()

        # Loop over experiments to delete until "N" given or timeout after 60 secs
        while True:
            i, o, e = select.select([sys.stdin], [], [], 60)
            if i:
                e_id = sys.stdin.readline().strip()
                if e_id == "N":
                    return e_id
            else:
                break

            if e_id not in self.experiment_ids:
                time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
                print(
                    "\n{} The e_id is not in the protocol db. "
                    "Please try again: [e_id/N]".format(time_t),
                    end=" ",
                )
                sys.stdout.flush()
                continue

            # Delete the dictionary in DB corresponding to e-id
            if action == "delete":
                self.delete(e_id, save=True)
            elif action == "abort":
                self.abort(e_id, save=True)
            else:
                return e_id

            print(
                "{} Another one? - state the next id: [e_id/N]".format(time_t),
                end=" ",
            )
            sys.stdout.flush()

    def ask_for_purpose(self):
        """Ask user for purpose of experiment."""
        # Add purpose of experiment - cmd args or timeout input after 30 secs
        time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        print(f"{time_t} Purpose of experiment?", end=" "),
        sys.stdout.flush()
        i, o, e = select.select([sys.stdin], [], [], 60)

        if i:
            purpose = sys.stdin.readline().strip()
        else:
            purpose = "default"
        return purpose
