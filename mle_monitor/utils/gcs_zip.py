import os
import glob
import zipfile
from typing import Union
from google.cloud import storage
from .helpers import setup_logger


def send_dir_gcp(
    cloud_settings: dict,
    local_dir: Union[str, None] = None,
    number_of_connect_tries: int = 5,
):
    """Send entire dir (recursively) to Google Cloud Storage Bucket."""
    logger = setup_logger()
    for i in range(number_of_connect_tries):
        try:
            client = storage.Client(cloud_settings["project_name"])
            bucket = client.get_bucket(cloud_settings["bucket_name"], timeout=20)
        except Exception:
            logger.info(
                f"Attempt {i+1}/{number_of_connect_tries}"
                " - Failed sending to GCloud Storage"
            )

    def upload_single_file(local_path, gcs_path, bucket):
        # Recursively upload the folder structure
        if os.path.isdir(local_path):
            for local_file in glob.glob(os.path.join(local_path, "**")):
                if not os.path.isfile(local_file):
                    upload_single_file(
                        local_file,
                        os.path.join(gcs_path, os.path.basename(local_file)),
                        bucket,
                    )
                else:
                    remote_path = os.path.join(
                        gcs_path, local_file[1 + len(local_path) :]
                    )
                    blob = bucket.blob(remote_path)
                    blob.upload_from_filename(local_file)
        # Only upload single file - e.g. zip compressed experiment
        else:
            remote_path = gcs_path
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)

    if local_dir is None:
        local_dir = os.getcwd()
    upload_single_file(local_dir, cloud_settings["remote_dir"], bucket)


def copy_dir_gcp(
    cloud_settings: dict,
    remote_dir: str,
    local_dir: Union[str, None] = None,
    number_of_connect_tries: int = 5,
):
    """Download entire dir (recursively) from Google Cloud Storage Bucket."""
    logger = setup_logger()

    for i in range(number_of_connect_tries):
        try:
            client = storage.Client(cloud_settings["project_name"])
            bucket = client.get_bucket(cloud_settings["bucket_name"], timeout=20)
        except Exception:
            logger.info(
                f"Attempt {i+1}/{number_of_connect_tries}"
                f" - Failed sending to GCloud Storage"
            )

    blobs = bucket.list_blobs(prefix=remote_dir)  # Get list of files
    blobs = list(blobs)

    if local_dir is None:
        path = os.path.normpath(remote_dir)
        local_dir = path.split(os.sep)[-1]

    # Recursively download the folder structure
    if len(blobs) > 1:
        local_path = os.path.expanduser(local_dir)
        for blob in blobs:
            filename = blob.name[len(remote_dir) :]
            local_f_path = os.path.join(local_path, filename)
            dir_path = os.path.dirname(local_f_path)

            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except Exception:
                    pass
            temp_file = local_path + filename
            temp_dir = os.path.split(temp_file)[0]
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            blob.download_to_filename(temp_file)
    # Only download single file - e.g. zip compressed experiment
    else:
        for blob in blobs:
            filename = blob.name.split("/")[1]
            blob.download_to_filename(filename)


def zipdir(path: str, zip_fname: str):
    """Zip a directory to upload afterwards to GCloud Storage."""
    # ziph is zipfile handle
    ziph = zipfile.ZipFile(zip_fname, "w", zipfile.ZIP_DEFLATED)
    # Get rid of redundant part of path
    prefix_len = len(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file), os.path.join(root[prefix_len + 1 :], file)
            )
    ziph.close()


def send_gcloud_zip(
    cloud_settings: dict,
    local_fname: str,
    local_zip_fname: str,
    delete_after_upload: bool = True,
):
    """Zip & upload experiment dir to Gcloud storage."""
    # 1. Get experiment hash from the protocol db
    gcloud_hash_fname = "experiments/" + local_zip_fname

    # 2. Zip compress the experiment
    zipdir(local_fname, local_zip_fname)

    # 3. Upload the zip file to the GCS bucket
    cloud_settings["remote_dir"] = gcloud_hash_fname
    send_dir_gcp(cloud_settings, local_zip_fname)

    # 4. Delete the .zip file & the folder if desired
    if delete_after_upload:
        os.remove(local_zip_fname)


def get_gcloud_zip(
    cloud_settings: dict,
    hash_to_store: str,
    experiment_id: str,
    local_dir_name: Union[None, str] = None,
):
    """Download zipped experiment from GCS. Unpack & clean up."""
    logger = setup_logger()
    # Get unique hash id & download the experiment results folder
    local_hash_fname = hash_to_store + ".zip"
    gcloud_hash_fname = "experiments/" + local_hash_fname
    copy_dir_gcp(cloud_settings, gcloud_hash_fname)

    # Unzip the retrieved file
    if local_dir_name is None:
        with zipfile.ZipFile(local_hash_fname, "r") as zip_ref:
            zip_ref.extractall(experiment_id)
    else:
        with zipfile.ZipFile(local_hash_fname, "r") as zip_ref:
            zip_ref.extractall(local_dir_name)

    # Delete the zip file
    os.remove(local_hash_fname)

    # Goodbye message if successful
    logger.info(f"Successfully retrieved {experiment_id}" f" - from GCS")
    logger.info(f"Remote Path: {gcloud_hash_fname}")
    return
