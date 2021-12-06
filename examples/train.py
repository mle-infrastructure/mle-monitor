import argparse
import random
from mle_logging import MLELogger
from mle_logging.utils import load_yaml_config


def train_your_net(epoch: int, seed_id: int, lrate: float, batch_size: int, arch: str):
    """Optimum: lrate=0.2, batch_size=4, arch='conv'."""
    f1 = (lrate - 0.2) ** 2 + (batch_size - 4) ** 2 + (0 if arch == "conv" else 10)
    train_loss = f1 + seed_id * 0.5
    test_loss = f1 + seed_id * 0.5 + random.uniform(0, 0.3)
    return train_loss / epoch, test_loss / epoch


def main(experiment_dir: str, config_fname: str, seed_id: int):
    """Example training 'loop' using MLE-Logging."""
    train_config = load_yaml_config(config_fname)
    log = MLELogger(
        experiment_dir=experiment_dir,
        config_fname=config_fname,
        seed_id=seed_id,
        time_to_track=["num_epochs"],
        what_to_track=["train_loss", "test_loss"],
    )
    for epoch in range(1, 11):
        train_loss, test_loss = train_your_net(epoch, seed_id, **train_config)
        log.update(
            {"num_epochs": epoch},
            {"train_loss": train_loss, "test_loss": test_loss},
            save=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Let's train a network.")
    parser.add_argument(
        "-exp_dir", "--experiment_dir", type=str, default="experiments/"
    )
    parser.add_argument(
        "-config", "--config_fname", type=str, default="base_config_1.yaml"
    )
    parser.add_argument("-seed", "--seed_id", type=int, default=1)
    args = vars(parser.parse_args())
    main(args["experiment_dir"], args["config_fname"], args["seed_id"])
