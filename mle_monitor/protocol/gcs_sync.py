import logging
import os
from os.path import expanduser
from ..utils import setup_logger
from google.cloud import storage


def set_gcp_credentials(credentials_path: str = ""):
    if credentials_path != "":
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
            credentials_path
        )


def get_gcloud_db(
    project_name: str,
    bucket_name: str,
    gcs_protocol_fname: str,
    local_protocol_fname: str,
    number_of_connect_tries: int = 5,
) -> int:
    """Pull latest experiment database from gcloud storage."""
    logger = setup_logger()
    for i in range(number_of_connect_tries):
        try:
            # Connect to project and bucket
            client = storage.Client(project_name)
            bucket = client.get_bucket(bucket_name, timeout=20)
            # Download blob to db file
            blob = bucket.blob(gcs_protocol_fname)
            with open(expanduser(local_protocol_fname), "wb") as file_obj:
                blob.download_to_file(file_obj)
            logger.info(f"Pulled from GCloud Storage - " f"{gcs_protocol_fname}")
            return 1
        except Exception as ex:
            # Remove empty file - causes error otherwise when trying to load
            os.remove(expanduser(local_protocol_fname))
            if type(ex).__name__ == "NotFound":
                logger.info(f"No DB found in GCloud Storage" f" - {gcs_protocol_fname}")
                logger.info(
                    "New DB will be created - " f"{project_name}/" f"{bucket_name}"
                )
                return 1
            else:
                logger.info(
                    f"Attempt {i+1}/{number_of_connect_tries}"
                    f" - Failed pulling from GCloud Storage"
                    f" - {type(ex).__name__}"
                )
    # If after 5 pulls no successful connection established - return failure
    return 0


def send_gcloud_db(
    project_name: str,
    bucket_name: str,
    gcs_protocol_fname: str,
    local_protocol_fname: str,
    number_of_connect_tries: int = 5,
):
    """Send updated database back to gcloud storage."""
    logger = setup_logger()
    for i in range(number_of_connect_tries):
        try:
            # Connect to project and bucket
            client = storage.Client(project_name)
            bucket = client.get_bucket(bucket_name, timeout=20)
            blob = bucket.blob(gcs_protocol_fname)
            blob.upload_from_filename(filename=expanduser(local_protocol_fname))
            logger.info(f"Send to GCloud Storage - " f"{gcs_protocol_fname}")
            return 1
        except Exception:
            logger.info(
                f"Attempt {i+1}/{number_of_connect_tries}"
                f" - Failed sending to GCloud Storage"
            )
    # If after 5 pulls no successful connection established - return failure
    return 0
