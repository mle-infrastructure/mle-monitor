from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
import datetime as dt


def layout_dashboard(resource: str, use_gcs_sync: bool, protocol_fname: str) -> Layout:
    """Define the MLE-Toolbox `monitor` base dashboard layout."""
    layout = Layout(name="root")
    # Split in three vertical sections: Welcome, core info, help + util plots
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="main"),
    )
    # Split center into 3 horizontal sections
    layout["main"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=8),
    )

    # Split center into 3 horizontal sections
    layout["right"].split_column(
        Layout(name="top-right", ratio=6),
        Layout(name="bottom-right", ratio=2),
    )

    # Split center into 3 horizontal sections
    layout["top-right"].split_row(
        Layout(name="top-right-left", ratio=6),
        Layout(name="top-right-right", ratio=2),
    )

    # Split center right into total experiments, last experiments, ETA
    layout["top-right-right"].split_column(
        Layout(name="top-right-right-1", ratio=3),
        Layout(name="top-right-right-2", ratio=3),
        Layout(name="top-right-right-3", ratio=4),
    )

    # Split bottom into toolbox command info and cluster util termplots
    layout["bottom-right"].split_row(
        Layout(name="bottom-right-1", ratio=1),
        Layout(name="bottom-right-2", ratio=1),
        Layout(name="bottom-right-3", ratio=1),
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
            "[bold]General Settings :bulb:",
            Header.welcome_ascii[0],
            "[bold]" + dt.datetime.now().ctime().replace("  ", " ") + " :alarm_clock:",
        )
        grid.add_row(
            "\u2022 GCS Sync Protocol: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Protocol: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[1],
            "Author: [u link=https://twitter.com/RobertTLange]@RobertTLange[/] :bird:",
        )

        grid.add_row(
            "\u2022 GCS Sync Results: [green]:heavy_check_mark:"
            if self.use_gcs_sync
            else "\u2022 GCS Sync Results: [red]:heavy_multiplication_x:",
            Header.welcome_ascii[2],
            ":point_right: [u link=https://github.com/mle-infrastructure]MLE-Infrastructure[/] :small_red_triangle:",
        )
        grid.add_row(
            f"\u2022 DB Path: {self.protocol_fname}",
            Header.welcome_ascii[3],
            f"Resource: {self.resource.resource_name} :computer:",
        )
        grid.add_row(
            "[bold]Carpe Diem[/bold] :city_sunrise:",
            Header.welcome_ascii[4],
            "[bold]Hi there - You rock!  [not italic]:hugging_face:[/]",
        )
        return Panel(grid, style="white on blue")
