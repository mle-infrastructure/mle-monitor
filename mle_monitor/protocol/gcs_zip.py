import os
import zipfile
from datetime import datetime
from typing import Union
from mle_scheduler.cloud.gcp import send_dir_gcp, copy_dir_gcp


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

    time_t = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    # Goodbye message if successful
    print(
        time_t,
        f"Successfully retrieved {experiment_id}" f" - from GCS",
    )
    print(time_t, f"Remote Path: {gcloud_hash_fname}")
    return
