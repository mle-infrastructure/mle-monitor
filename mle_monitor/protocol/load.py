import re
import pickledb


def load_protocol_db(protocol_fname):
    """Load local database from config name & reconstruct experiment id."""
    # Attempt loading local protocol database - otherwise return clean one
    db = pickledb.load(protocol_fname, False, sig=False)
    # Get the most recent experiment id
    all_experiment_ids = list(db.getall())
    try:
        all_experiment_ids.remove("summary")
    except:
        pass

    def natural_keys(text: str):
        """Helper function for sorting alpha-numeric strings."""

        def atoi(text):
            return int(text) if text.isdigit() else text

        return [atoi(c) for c in re.split(r"(\d+)", text)]

    # Sort experiment ids & get the last one
    if len(all_experiment_ids) > 0:
        all_experiment_ids.sort(key=natural_keys)
        last_experiment_id = int(all_experiment_ids[-1])
    else:
        last_experiment_id = 0
    return db, all_experiment_ids, last_experiment_id
