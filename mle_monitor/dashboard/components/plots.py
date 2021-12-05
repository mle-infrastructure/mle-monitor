import numpy as np
import plotext as plt
from rich.ansi import AnsiDecoder
from rich.align import Align
from rich.table import Table


def make_cpu_util_plot(cpu_hist) -> Align:
    """Plot curve displaying a CPU usage times series for the cluster."""
    x = np.arange(len(cpu_hist["rel_cpu_util"])).tolist()
    y = np.array(cpu_hist["rel_cpu_util"]).tolist()

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, marker="dot", color="red", label="% CPU Util.")
    plt.figure.plot_size(40, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(cpu_hist["times_hour"]) - 1]
    xlabels = [
        cpu_hist["times_date"][i][:5] + "-" + cpu_hist["times_hour"][i] for i in xticks
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


def make_memory_util_plot(mem_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    x = np.arange(len(mem_hist["rel_mem_util"])).tolist()
    y = np.array(mem_hist["rel_mem_util"]).tolist()

    # Clear the plot and draw the utilisation lines
    plt.clear_plot()
    plt.plot(x, y, marker="dot", color="red", label="% Memory Util.")
    plt.figure.plot_size(40, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.ylim(0, 1)

    # Get time points start and end of monitored period
    xticks = [0, len(mem_hist["times_hour"]) - 1]
    xlabels = [
        mem_hist["times_date"][i][:5] + "-" + mem_hist["times_hour"][i] for i in xticks
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


def make_protocol_total_plot(exp_total_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    plt.clear_plot()
    plt.datetime.set_datetime_form(date_form="%m/%d/%y %H:%M")

    prices = [
        1763.0,
        1740.3,
        1752.7,
        1749.8,
        1777.0,
    ]
    dates = [
        "07/10/20 04:33",
        "07/13/20 04:33",
        "07/14/20 04:33",
        "07/15/20 04:33",
        "07/16/20 04:33",
    ]

    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")
    plt.plot_date(dates, prices, marker="dot", color="blue", label="1")
    plt.plot_date(
        dates, [p - 10 for p in prices], marker="dot", color="yellow", label="2"
    )
    plt.figure.plot_size(40, 9)
    plot_str = plotext_helper()
    decoder = AnsiDecoder()
    lines = list(decoder.decode(plot_str))

    # Build the rich table graph
    message = Table.grid()
    message.add_column()
    for line in lines:
        message.add_row(line)
    return Align.center(message)


def make_protocol_daily_plot(exp_daily_hist) -> Align:
    """Plot curve displaying a memory usage times series for the cluster."""
    pizzas = ["Sausage", "Pepperoni", "Mushrooms", "Cheese", "Chicken", "Beef"]
    male_percentages = [14, 36, 11, 8, 7, 4]
    female_percentages = [12, 20, 35, 15, 2, 1]
    plt.clear_plot()
    plt.stacked_bar(
        pizzas,
        [male_percentages, female_percentages],
        label=["men", "women"],
        marker="sd",
        color=["red", "yellow"],
    )
    plt.figure.plot_size(40, 9)
    plt.canvas_color("black")
    plt.axes_color("black")
    plt.ticks_color("white")

    # # Get time points start and end of monitored period
    # xticks = [0, len(mem_hist["times_hour"]) - 1]
    # xlabels = [
    #     mem_hist["times_date"][i][:5] + "-" + mem_hist["times_hour"][i] for i in xticks
    # ]
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
