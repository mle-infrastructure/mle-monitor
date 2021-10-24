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
        use_gcs_sync: bool = False,
        project_name: Union[str, None] = None,
        bucket_name: Union[str, None] = None,
        gcs_protocol_fname: Union[str, None] = None,
        local_protocol_fname: Union[str, None] = None,
        gcs_credentials_path: Union[str, None] = None,
    ):
        """MLE Protocol DB Instance."""
        self.protocol_fname = protocol_fname
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

    def get(self, experiment_id, var_name):
        """Retrieve variable from database."""
        return self.db.dget(experiment_id, var_name)

    def save(self, save: bool = True):
        """Dump the protocol db to its pickle file."""
        self.db.dump()

    def add(self, job_config, resource_to_run, cmd_purpose, save: bool = True):
        """Add an experiment to the database."""
        self.db, new_experiment_id, purpose = protocol_experiment(
            self.db, self.last_experiment_id, job_config, resource_to_run, cmd_purpose
        )
        if save:
            self.save()
        return new_experiment_id, purpose

    def abort(self, e_id, save: bool = True):
        """Abort an experiment - change status in db."""
        self.db.dadd(e_id, ("job_status", "aborted"))
        if save:
            self.save()

    def delete(self, e_id, save: bool = True):
        """Delete an experiment - change status in db."""
        self.db.drem(e_id)
        if save:
            self.save()

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
                self.db.dadd(experiment_id, (var_name[db_v_id], var_value[db_v_id]))
        else:
            self.db.dadd(experiment_id, (var_name, var_value))
        if save:
            self.save()

    def summary(self, tail: int = 5, verbose: bool = True, return_table: bool = False):
        """Print a rich summary table of all experiments in db."""
        summary = protocol_summary(self.db, self.experiment_ids, tail, verbose)
        if return_table:
            return protocol_table(summary)
        return summary

    def ask_user(self, delete: bool = False, abort: bool = False):
        """Ask user if they want to delete/abort previous experiment by id."""
        time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        if delete:
            q_str = "{} Want to delete experiment? - state its id: [e_id/N]"
        elif abort:
            q_str = "{} Want to abort experiment? - state its id: [e_id/N]"
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

            # Delete the dictionary in DB corresponding to e-id
            try:
                if delete:
                    self.delete(e_id, save=True)
                elif abort:
                    self.abort(e_id, save=True)

                print(
                    "{} Another one? - state the next id: [e_id/N]".format(time_t),
                    end=" ",
                )
            except Exception:
                print(
                    "\n{} The e_id is not in the protocol db. "
                    "Please try again: [e_id/N]".format(time_t),
                    end=" ",
                )
            sys.stdout.flush()

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
