import numpy as np
import plotext as plt
from rich.ansi import AnsiDecoder
from rich.align import Align
from rich.table import Table


def make_util_plot(util_hist) -> Align:
    """Plot curve displaying a CPU usage times series for the cluster."""
    x = np.arange(len(util_hist["rel_cpu_util"])).tolist()
    y = np.array(util_hist["rel_cpu_util"]).tolist()

    x_mem = np.arange(len(util_hist["rel_mem_util"])).tolist()
    y_mem = np.array(util_hist["rel_mem_util"]).tolist()
    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, marker="dot", color="red", label="% CPU Util.")
    plt.plot(x_mem, y_mem, marker="dot", color="yellow", label="% Mem Util.")
    plt.figure.plot_size(42, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(util_hist["times_hour"]) - 1]
    xlabels = [
        util_hist["times_date"][i][:5] + "-" + util_hist["times_hour"][i]
        for i in xticks
    ]
    plt.xticks(xticks, xlabels)
    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def make_protocol_total_plot(experiment_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    plt.clear_plot()
    plt.datetime.set_datetime_form(date_form="%m/%d/%y %H:%M")

    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.plot_date(
        experiment_hist["time"],
        experiment_hist["total_exp"]["all"],
        marker="dot",
        color="yellow",
        label="Total",
    )
    plt.figure.plot_size(42, 9)

    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def make_protocol_daily_plot(experiment_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    plt.clear_plot()
    try:
        day_short = [e[:5] for e in experiment_hist["day"]]
        # Add empty string for label legend visability
        plt.stacked_bar(
            [""] + day_short,
            [
                [0.1] + experiment_hist["day_exp"]["hyperparameter-search"],
                [0] + experiment_hist["day_exp"]["multiple-configs"],
                [0] + experiment_hist["day_exp"]["single-config"],
            ],
            label=["HS", "MC", "SC"],
            marker="sd",
            color=["yellow", "red", "blue"],
        )
    except Exception:
        pass
    plt.figure.plot_size(42, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")

    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def plotext_helper():
    """Helper fct. that generates ansi string  to plot."""
    plt.figure.build()
    return plt.figure.canvas
