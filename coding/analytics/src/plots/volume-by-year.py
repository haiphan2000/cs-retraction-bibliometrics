import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image
from src.plotting_styles import *
from src.utils import *

TARGET_IMAGE_WIDTH = 3353
CHART_WIDTH = 10

def prepare_chart_data(
    df: pd.DataFrame,
) -> tuple[list[str], list[int], int, list[int], int]:
    """Extract and format chart data, positions, and dynamic Y-axis bounds.

    Args:
        df: DataFrame containing 'retraction_year' and 'retraction_count'.

    Returns:
        A tuple containing (x_labels, y_counts, n_points, x_range, y_limit).
    """
    x_labels = [str(year) for year in df["retraction_year"].unique()]

    y_counts = df["retraction_count"].tolist()
    n_points = len(x_labels)
    x_range = list(range(n_points))

    step = 100
    max_y = max(y_counts, default=0)
    y_limit = (max_y // step + 1) * step

    return x_labels, y_counts, n_points, x_range, y_limit

def create_chart_figure(
    figsize: tuple[float, float] = (CHART_WIDTH-2.0, 5.0)
) -> tuple[Figure, Axes]:
    """Initialize a Matplotlib figure and axis with configurable plot margins.

    Args:
        figsize: Figure dimensions in inches (width, height). Defaults to (10.0, 6.09).
        dpi: Figure resolution in dots per inch. Defaults to 110.
        margins: Dictionary containing plot margin adjustments ('left', 'right',
            'top', 'bottom'). Uses DEFAULT_MARGINS if None.

    Returns:
        A tuple containing (Figure, Axes).
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(
        left=0.12,
        right=0.82,
        top=0.72,
        bottom=0.18,
    )

    return fig, ax

def plot_trend_lines(
    ax: Axes,
    x_range: list[int],
    y_counts: list[int],
    n_points: int,
    palette: dict[str, str]
) -> None:
    """Plot gray baseline, solid blue trend, and dashed blue projection lines (PCHIP Smooth)."""
    if n_points < 2:
        return

    x_arr = np.array(x_range)
    y_arr = np.array(y_counts)

    line_segments = [
        (0, 3, "GRAY_DARK", "-", 2),
        (2, 5, "blue_primary", "-", 6),
        (4, 6, "blue_primary", "-", 6),
    ]

    for start, end, color_key, linestyle, min_points in line_segments:
        if n_points < min_points:
            continue

        end_idx = min(end - 1, n_points - 1)

        if start > end_idx:
            continue

        # Cắt trực tiếp mảng x và y thay vì dùng PCHIP
        x_segment = x_arr[start : end_idx + 1]
        y_segment = y_arr[start : end_idx + 1]

        ax.plot(
            x_segment,
            y_segment,
            linewidth=4.0,
            color=palette[color_key],
            linestyle=linestyle,
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=3,
        )

def plot_data_markers(
    ax: Axes,
    x_range: list[int],
    y_counts: list[int],
    n_points: int,
    palette: dict[str, str]
) -> None:
    """Plot filled intermediate circles and an unfilled final circle marker.

    Args:
        ax: Matplotlib Axes object to draw on.
        x_range: List of X-axis integer positions.
        y_counts: List of Y-axis numeric data values.
        n_points: Total number of available data points.
        palette: Color palette dictionary mapping line names to hex codes.
    """
    if not x_range or not y_counts:
        return

    filled_indices = [
        idx for idx in (2, 3, 4, 5)
        if idx < n_points
    ]

    if filled_indices:
        x_filled = [x_range[idx] for idx in filled_indices]
        y_filled = [y_counts[idx] for idx in filled_indices]

        ax.scatter(
            x_filled,
            y_filled,
            s=90,
            color=palette["blue_primary"],
            clip_on=False,
            zorder=4,
        )

def add_data_labels(
    ax: Axes,
    x_range: list[int],
    y_counts: list[int],
    n_points: int,
    positions: dict[int, tuple[tuple[int, int], str, str]],
    palette: dict[str, str]
) -> None:
    """Annotate each data point with its numeric value.

    Args:
        ax: Matplotlib Axes object to draw annotations on.
        x_range: List of X-axis integer positions.
        y_counts: List of Y-axis numeric data values.
        n_points: Total number of available data points.
        positions: Mapping of point index to layout configs: (xytext, ha, va).
        palette: Color palette dictionary mapping text names to hex codes.
    """
    for idx, (x_val, y_val) in enumerate(zip(x_range, y_counts)):
        text_color = (
            palette["GRAY_DARK"]
            if idx in (0, 1)
            else palette["blue_primary"]
        )

        font_weight = "bold"

        if idx == n_points - 1:
            xytext = (10, 0)
            ha = "left"
            va = "center"
        else:
            xytext, ha, va = positions.get(
                idx,
                ((0, 6), "center", "bottom"),
            )

        ax.annotate(
            text=str(y_val),
            xy=(x_val, y_val),
            xytext=xytext,
            textcoords="offset points",
            ha=ha,
            va=va,
            color=text_color,
            fontsize=DEFAULT_FONT_SIZE,
            fontweight=font_weight,
        )

def draw_vertical_reference_line(
    ax: Axes,
    fig: Figure,
    x_val: float,
    y_val: float,
    palette: dict[str, str],
    offset_cm
) -> None:
    """Draw a vertical dashed line extending above a data point.

    Args:
        ax: Matplotlib Axes target object.
        fig: Matplotlib Figure parent object.
        x_val: X-coordinate for vertical line anchor.
        y_val: Y-coordinate for top reference marker point.
        palette: Dictionary containing hex color strings.
        offset_cm: Vertical height extension above point in cm.
    """
    # Convert centimeter offset to pixels (1 inch = 2.54 cm)
    offset_pixels = (offset_cm / 2.54) * fig.dpi

    # Transform data coordinates to pixel space and calculate the top limit
    _, y_px = ax.transData.transform((x_val, y_val))
    y_top_px = y_px + offset_pixels

    # Convert pixel top limit back into data space coordinates
    _, y_top = ax.transData.inverted().transform((0, y_top_px))

    ax.vlines(
        x=x_val,
        ymin=0,
        ymax=y_top,
        color=palette["blue_primary"],
        linestyle=(0,(2,1)),
        linewidth=3.0,
        zorder=1,
    )

def draw_stepped_arrow(
    ax: Axes,
    x_start: float,
    y_start: float,
    x_end: float,
    y_end: float,
    palette: dict[str, str],
    label_text: str | None = None,
) -> None:
    """Draw a stepped elbow arrow (horizontal -> vertical) with an inline label.

    Args:
        ax: Matplotlib Axes target object.
        x_start: Starting X-axis coordinate.
        y_start: Starting Y-axis coordinate.
        x_end: Ending X-axis coordinate.
        y_end: Ending Y-axis coordinate.
        palette: Dictionary containing hex color strings.
        label_text: Optional text label. Calculated dynamically if None.
    """
    if label_text is None and y_start != 0:
        pct_change = ((y_end - y_start) / y_start) * 100
        if pct_change < 0:
            label_text = f"\u2212{abs(pct_change):.2f}%"
        else:
            label_text = f"+{pct_change:.2f}%"

    # 1. Draw horizontal segment
    ax.annotate(
        text="",
        xy=(x_end, y_start),
        xytext=(x_start, y_start),
        arrowprops=dict(
            arrowstyle="-",
            color=palette["gray_text"],
            linewidth=3.0,
            shrinkA=8,
            shrinkB=0,
        ),
        zorder=5,
    )

    # 2. Draw vertical arrow segment
    ax.annotate(
        text="",
        xy=(x_end, y_end),
        xytext=(x_end, y_start),
        arrowprops=dict(
            arrowstyle="->",
            color=palette["gray_text"],
            linewidth=3.0,
            mutation_scale=20,
            shrinkA=0,
            shrinkB=8,
        ),
        zorder=5,
    )

    # 3. Draw inline text label at midpoint of horizontal segment
    if label_text:
        x_mid = (x_start + x_end) / 2
        ax.text(
            x=x_mid,
            y=y_start,
            s=label_text,
            ha="center",
            va="center",
            fontsize=DEFAULT_FONT_SIZE,
            color=palette["gray_text"],
            fontweight="bold",
            zorder=6,
            bbox=dict(
                boxstyle="square,pad=0.3",
                facecolor="white",
                edgecolor="none",
            ),
        )

def add_trend_annotations(
    ax: Axes,
    fig: Figure,
    x_range: list[int],
    y_counts: list[int],
    x_labels: list[str],
    palette: dict[str, str],
) -> None:
    """Locate the 2023 data point and draw a reference line with a stepped arrow.

    Args:
        ax: Matplotlib Axes target object.
        fig: Matplotlib Figure parent object.
        x_range: Positional integer sequence for X-axis.
        y_counts: Numeric data point values.
        x_labels: Display labels for X-axis categories.
        palette: Dictionary containing hex color strings.
    """
    x_2023_idx = next(
        (i for i, label in enumerate(x_labels) if "2023" in label), None
    )

    if x_2023_idx is not None and len(x_range) >= 3:
        x_2023, y_2023 = x_range[x_2023_idx], y_counts[x_2023_idx]
        x_final, y_final = x_range[-1], y_counts[-1]

        draw_vertical_reference_line(
            ax=ax,
            fig=fig,
            x_val=x_2023,
            y_val=y_2023,
            palette=palette,
            offset_cm=2.00,
        )
        draw_stepped_arrow(
            ax=ax,
            x_start=x_2023,
            y_start=y_2023,
            x_end=x_final,
            y_end=y_final,
            palette=palette,
        )

def format_axes_and_spines(
    ax: Axes,
    fig: Figure,
    x_range: list[int],
    x_labels: list[str],
    y_limit: int,
    palette: dict[str, str],
) -> None:
    """Set axis bounds, tick values, offsets, and hide top/right spines.

    Args:
        ax: Matplotlib Axes target object.
        fig: Matplotlib Figure parent object.
        x_range: Positional integer sequence for X-axis.
        x_labels: Display labels for X-axis categories.
        y_limit: Upper numerical bound for Y-axis.
        palette: Dictionary containing hex color strings.
    """
    n_points = len(x_range)
    ax.set_xlim(-0.4, max(1, n_points - 1) + 0.4)
    ax.set_ylim(0, y_limit)

    # Only set X-axis ticks and labels; clear Y-axis ticks/values
    ax.set_xticks(x_range)
    ax.set_xticklabels(x_labels)

    ax.tick_params(bottom=False)

    # Hide top, left, and right spines, but keep the bottom spine (X-axis line) visible
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(True)

def add_chart_titles(
    ax: Axes,
    y_limit: int,
    n_points: int,
    palette: dict[str, str],
) -> None:
    """Add chart title, Y-axis label, and publisher note annotation.

    Args:
        ax: Matplotlib Axes target object.
        y_limit: Upper numerical bound for Y-axis.
        n_points: Total count of data points available.
        palette: Dictionary containing hex color strings.
    """
    if n_points >= 2:
        annotation_x = max(0, n_points - min(n_points, 4) + 0.1)
        ax.text(
            x=annotation_x,
            y=y_limit * 0.9,
            s="Publisher mass retraction",
            fontsize=18,
            color=palette["blue_primary"],
            linespacing=1.4,
        )

def render_retraction_chart(
    df: pd.DataFrame,
    palette: dict[str, str],
    annotation_positions: dict[int, tuple[tuple[int, int], str, str]],
) -> tuple[Figure, Axes]:
    """Orchestrate chart creation by delegating tasks to visualization helpers.

    Args:
        df: DataFrame containing retraction metric source data.
        palette: Dictionary containing hex color strings.
        annotation_positions: Dictionary mapping point indices to offset specs.

    Returns:
        A tuple containing the generated (fig, ax) objects.
    """
    x_labels, y_counts, n_points, x_range, y_limit = prepare_chart_data(df)
    fig, ax = create_chart_figure()

    plot_trend_lines(
        ax=ax,
        x_range=x_range,
        y_counts=y_counts,
        n_points=n_points,
        palette=palette,
    )
    plot_data_markers(
        ax=ax,
        x_range=x_range,
        y_counts=y_counts,
        n_points=n_points,
        palette=palette,
    )
    add_data_labels(
        ax=ax,
        x_range=x_range,
        y_counts=y_counts,
        n_points=n_points,
        positions=annotation_positions,
        palette=palette,
    )
    add_trend_annotations(
        ax=ax,
        fig=fig,
        x_range=x_range,
        y_counts=y_counts,
        x_labels=x_labels,
        palette=palette,
    )
    format_axes_and_spines(
        ax=ax,
        fig=fig,
        x_range=x_range,
        x_labels=x_labels,
        y_limit=y_limit,
        palette=palette,
    )
    add_chart_titles(
        ax=ax,
        y_limit=y_limit,
        n_points=n_points,
        palette=palette,
    )

    file_path = "output/volume-by-year.png"
    fig.savefig(
        file_path,
        bbox_inches="tight",
    )

    return fig, ax

ANNOTATION_POSITIONS = {
    1: ((0, -15), "center", "top"),
    2: ((-10, 8), "right", "center"),
    3: ((0, -10), "center", "top"),
}

print("Done")