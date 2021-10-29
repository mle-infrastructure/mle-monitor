from typing import Union, List
from datetime import datetime
import sys
import select
from .protocol import (
    load_protocol_db,
    protocol_summary,
    protocol_experiment,
    protocol_table,
    get_monitor_db_data,
)


class MLEProtocol(object):
    def __init__(
        self,
        protocol_fname: str,
        extra_keys: Union[None, List[str]] = None,
        use_gcs_sync: bool = False,
        project_name: Union[str, None] = None,
        bucket_name: Union[str, None] = None,
        gcs_protocol_fname: Union[str, None] = None,
        local_protocol_fname: Union[str, None] = None,
        gcs_credentials_path: Union[str, None] = None,
    ):
        """MLE Protocol DB Instance."""
        self.protocol_fname = protocol_fname
        self.extra_keys = extra_keys
        self.use_gcs_sync = use_gcs_sync
        self.project_name = project_name
        self.bucket_name = bucket_name
        self.gcs_protocol_fname = gcs_protocol_fname
        self.local_protocol_fname = local_protocol_fname
        self.gcs_credentials_path = gcs_credentials_path

        if self.use_gcs_sync:
            from .protocol.gcs_sync import set_gcp_credentials

            # Set the path to the GCP credentials json file & pull recent db
            set_gcp_credentials(self.gcs_credentials_path)
        self.load()

    def load(self, pull_gcs: bool = True):
        """Load the protocol data from a local pickle file."""
        if self.use_gcs_sync:
            if pull_gcs:
                self.accessed_gcs = self.gcs_pull()
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

    def save(self, save: bool = True):
        """Dump the protocol db to its pickle file."""
        self.db.dump()

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

    def add(self, standard: dict, extra: Union[dict, None] = None, save: bool = True):
        """Add an experiment to the database."""
        for k in self.standard_keys:
            assert k in standard.keys()
        if extra is not None:
            for k in self.extra_keys:
                assert k in extra.keys()
        self.db, new_experiment_id = protocol_experiment(
            self.db, self.last_experiment_id, standard, extra
        )
        self.experiment_ids.append(new_experiment_id)
        self.last_experiment_id = new_experiment_id
        if save:
            self.save()
        return new_experiment_id

    def abort(self, experiment_id: Union[int, str], save: bool = True):
        """Abort an experiment - change status in db."""
        self.db.dadd(str(experiment_id), ("job_status", "aborted"))
        if save:
            self.save()

    def delete(self, experiment_id: Union[int, str], save: bool = True):
        """Delete an experiment - change status in db."""
        self.db.drem(str(experiment_id))
        if save:
            self.save()

    def status(self, experiment_id: Union[int, str]) -> str:
        """Get the status of an experiment."""
        return self.db.dget(str(experiment_id), "job_status")

    def update(
        self,
        experiment_id: str,
        var_name: Union[List[str], str],
        var_value: Union[list, str, dict],
        save: bool = True,
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
            self.save()

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
        protocol_table = self.summary(tail=29, verbose=False, return_table=True)
        return total_data, last_data, time_data, protocol_table

    def gcs_send(self):
        """Send the local protocol to a GCS bucket."""
        from .protocol.gcs_sync import send_gcloud_db

        send_db = send_gcloud_db(
            self.project_name,
            self.bucket_name,
            self.gcs_protocol_fname,
            self.local_protocol_fname,
        )
        return send_db

    def gcs_pull(self):
        """Pull the remote protocol from a GCS bucket."""
        from .protocol.gcs_sync import get_gcloud_db

        accessed_db = get_gcloud_db(
            self.project_name,
            self.bucket_name,
            self.gcs_protocol_fname,
            self.local_protocol_fname,
        )
        return accessed_db

    def __len__(self) -> int:
        """Return number of experiments stored in protocol."""
        return len(self.experiment_ids)

    def ask_for_e_id(self, action_str: str = "delete"):
        """Ask user if they want to delete/abort previous experiment by id."""
        time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        q_str = "{} Want to {} an experiment? - state its id: [e_id/N]"
        print(q_str.format(time_t, action_str), end=" ")
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
            if action_str == "delete":
                self.delete(e_id, save=True)
            elif action_str == "abort":
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
