from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
import datetime as dt


def layout_mle_dashboard(
    resource: str, use_gcs_sync: bool, protocol_fname: str
) -> Layout:
    """Define the MLE-Toolbox `monitor` base dashboard layout."""
    layout = Layout(name="root")
    # Split in three vertical sections: Welcome, core info, help + util plots
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="main", ratio=3),
        Layout(name="footer", ratio=1),
    )
    # Split center into 3 horizontal sections
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="center", ratio=3),
        Layout(name="right", ratio=1),
    )

    # Split center right into total experiments, last experiments, ETA
    layout["right"].split_column(
        Layout(name="r-box1", ratio=3),
        Layout(name="r-box2", ratio=3),
        Layout(name="r-box3", ratio=4),
    )
    # Split bottom into toolbox command info and cluster util termplots
    layout["footer"].split_row(
        Layout(name="f-box1", ratio=1),
        Layout(name="f-box2", ratio=1),
        Layout(name="f-box3", ratio=1),
        Layout(name="f-box4", ratio=1),
    )
    # # Fill the header with life!
    layout["header"].update(Header(resource, use_gcs_sync, protocol_fname))
    return layout


class Header:
    """Display header with clock and general toolbox configurations."""

    welcome_ascii = """                        __                                 _ __
             ____ ___  / /__        ____ ___  ____  ____  (_) /_____  _____
            / __ `__ \/ / _ \______/ __ `__ \/ __ \/ __ \/ / __/ __ \/ ___/
           / / / / / / /  __/_____/ / / / / / /_/ / / / / / /_/ /_/ / /
          /_/ /_/ /_/_/\___/     /_/ /_/ /_/\____/_/ /_/_/\__/\____/_/
""".splitlines()

    def __init__(self, resource: str, use_gcs_sync: bool, protocol_fname: str):
        self.resource = resource
        self.use_gcs_sync = use_gcs_sync
        self.protocol_fname = protocol_fname

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            "General Settings:",
            Header.welcome_ascii[0],
            dt.datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        grid.add_row(
            "\u2022 GCS Sync Protocol: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Protocol: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[1],
            "Author: @RobertTLange :bird:",
            # [u white link=https://twitter.com/RobertTLange]
        )

        grid.add_row(
            "\u2022 GCS Sync Results: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Results: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[2],
            f"Resource: {self.resource.resource_name}",
        )
        grid.add_row(
            f"\u2022 DB Path: {self.protocol_fname}",
            Header.welcome_ascii[3],
            "Hi there! [not italic]:hugging_face:[/]",
        )
        grid.add_row(
            "",
            Header.welcome_ascii[4],
            "",
        )
        return Panel(grid, style="white on blue")
