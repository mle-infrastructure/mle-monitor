from rich import box
from rich.table import Table
from rich.spinner import Spinner


def generate_protocol_table(df, full=True):
    """Generate pretty table of experiment protocol db - preselected db."""
    table = Table(show_header=True, show_footer=False, header_style="bold blue")
    sta_str = "[green]:heavy_check_mark:[/green]/[red]:heavy_multiplication_x:"
    table.add_column(sta_str, justify="center")
    table.add_column("E-ID")
    table.add_column("Date")
    table.add_column("Project")
    table.add_column("Purpose")
    table.add_column("Type")
    table.add_column("[yellow]:arrow_forward:", justify="center")

    # Full option prints also resource requirements of jobs
    if full:
        table.add_column("#Jobs", justify="center")
        table.add_column("#CPU", justify="center")
        table.add_column("#GPU", justify="center")
        table.add_column("[yellow]:recycle:", justify="center")

    # Add rows of info if dataframe exists (previously recorded experiments)
    if df is not None:
        for index in reversed(df.index):
            row = df.iloc[index]
            if row["Resource"] == "sge-cluster":
                resource = "SGE"
            elif row["Resource"] == "slurm-cluster":
                resource = "Slurm"
            elif row["Resource"] == "gcp-cloud":
                resource = "GCP"
            else:
                resource = "Local"

            if row["Status"] == "running":
                status = Spinner("dots", style="magenta")
            elif row["Status"] == "completed":
                status = "[green]:heavy_check_mark:"
            else:
                status = "[red]:heavy_multiplication_x:"

            if full:
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:20],
                    row["Purpose"][:25],
                    row["Type"],
                    resource,
                    str(row["Jobs"]),
                    str(row["CPUs"]),
                    str(row["GPUs"]),
                    str(row["Seeds"]),
                )
            else:
                table.add_row(
                    status,
                    row["ID"],
                    row["Date"],
                    row["Project"][:20],
                    row["Purpose"][:25],
                    row["Type"],
                    resource,
                )

    table.border_style = "blue"
    table.box = box.SIMPLE_HEAD
    return table
