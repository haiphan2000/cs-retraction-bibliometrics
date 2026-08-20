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
) -> tuple[list[str], pd.DataFrame, np.ndarray]:
    """Extract and calculate 100% stacked percentage distribution for authorship patterns by year.

    Args:
        df: DataFrame containing 'retraction_year' and count columns
            ('1 author', '2 authors', '3 authors', '4+ authors').

    Returns:
        A tuple containing (y_labels, df_pct, y_pos).
    """
    df = df.sort_values("retraction_year", ascending=False).reset_index(drop=True)

    df["retraction_year"] = df["retraction_year"].astype(str)

    y_labels = df["retraction_year"].tolist()

    value_cols = [
        "1 author",
        "2 authors",
        "3 authors",
        "4+ authors",
    ]
    counts = df[value_cols]
    df_pct = counts.div(counts.sum(axis=1), axis=0) * 100

    y_pos = np.arange(len(y_labels))
    return y_labels, df_pct, y_pos

def plot_stacked_horizontal_bars(
    ax: Axes,
    y_pos: np.ndarray,
    df_pct: pd.DataFrame,
    palette: dict[str, str],
) -> None:
    """Plot 100% stacked horizontal bars representing authorship pattern distribution.

    Args:
        ax: Matplotlib Axes object to draw on.
        y_pos: NumPy array of Y-axis positions.
        df_pct: DataFrame containing percentage values for each category.
        palette: Dictionary containing hex color strings.
    """
    categories = df_pct.columns.tolist()
    colors = [
        palette["blue_primary"],     # 1 author
        palette["gray_light"],  # 2 authors
        palette["gray_light_text"],  # 3 authors
        palette["GRAY_DARK"],        # 4 authors
    ]

    left = np.zeros(len(df_pct))

    for cat, color in zip(categories, colors):
        values = df_pct[cat].values
        ax.barh(
            y_pos,
            values,
            left=left,
            color=color,
            edgecolor=palette["white"],
            linewidth=1.5,
            height=0.8,
        )
        left += values

def format_authorship_axes_and_spines(
    ax: Axes,
    palette: dict[str, str],
    y_pos: np.ndarray,
    y_labels: list[str],
) -> None:
    """Configure axis limits, percentage ticks, custom text-based legend line, and labels.

    Args:
        ax: Matplotlib Axes target object.
        palette: Dictionary containing hex color strings.
        y_pos: NumPy array of Y-axis positions.
        y_labels: List of string year labels.
    """
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlim(0, 100)

    # Configure custom percentage ticks on x-axis
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels(
        ["0%", "20%", "40%", "60%", "80%", "100%"],
    )

    # Add "Percent of total" label above the x-axis ticks
    ax.text(
        -0.023, 1.13, "Percent of total",
        transform=ax.transAxes,
        color=palette["GRAY_DARK"],
        fontsize=DEFAULT_FONT_SIZE,
        fontweight="normal",
        va="bottom",
        ha="left"
    )

    # Add custom text-based legend line at the top with proper scaling
    categories = [
        "1 author",
        "2 authors",
        "3 authors",
        "4+ authors",
    ]
    colors = [
        palette["blue_primary"],
        palette["gray_light"],
        palette["gray_light_text"],
        palette["GRAY_DARK"],
    ]

    x_offset = -0.024
    y_legend = 1.23

    # Hệ số tỉ lệ co giãn khoảng cách dựa theo DEFAULT_FONT_SIZE để tránh chồng chữ
    font_scale = DEFAULT_FONT_SIZE / 10.0

    for i, (cat, color) in enumerate(zip(categories, colors)):
        if i > 0:
            ax.text(
                x_offset, y_legend, " | ",
                transform=ax.transAxes,
                color=palette["GRAY_DARK"],
                fontsize=DEFAULT_FONT_SIZE,
                fontweight="bold",
                va="bottom",
                ha="left"
            )
            x_offset += 0.022 * font_scale  # Khoảng cách an toàn cho dấu |

        ax.text(
            x_offset, y_legend, cat,
            transform=ax.transAxes,
            color=color,
            fontsize=DEFAULT_FONT_SIZE,
            fontweight="bold",  # In đậm toàn bộ các nhãn theo yêu cầu
            va="bottom",
            ha="left"
        )
        x_offset += len(cat) * 0.012 * font_scale  # Khoảng cách tự động giãn theo độ dài từ

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)

    ax.tick_params(axis="x", length=4)
    ax.tick_params(axis="y", length=0, pad=10)

    ax.spines["top"].set_color(palette["GRAY_DARK"])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)

def add_percentage_labels(
    ax: Axes,
    y_pos: np.ndarray,
    df_pct: pd.DataFrame,
) -> None:
    """Add percentage labels rounded to 1 decimal place, left-aligned,
    for '1 author' and '4+ authors' categories with white text color.
    """
    target_cats = ["1 author", "4+ authors"]
    left = np.zeros(len(df_pct))

    for cat in df_pct.columns:
        values = df_pct[cat].values
        if cat in target_cats:
            for idx, (val, l_val) in enumerate(zip(values, left)):
                # Chỉ hiển thị nhãn nếu giá trị phần trăm lớn hơn 0
                if val > 0:
                    pct_text = f"{val:.0f}%"

                    if cat == "1 author":
                        # Căn lề trái (cách mép trái của đoạn bar một chút)
                        x_pos = l_val + 1.5
                        ha_align = "left"
                    else:  # "4+ authors"
                        # Căn lề phải (cách mép phải của đoạn bar lùi vào trong một chút)
                        x_pos = l_val + values[idx] - 1.5
                        ha_align = "right"

                    ax.annotate(
                        pct_text,
                        xy=(x_pos, y_pos[idx]),
                        xytext=(0, -1),
                        textcoords="offset points",
                        ha=ha_align,
                        va="center",
                        color="white",
                        fontsize=ANNOTATION_FONT_SIZE,
                    )
        left += values

def render_authorship_distribution_chart(
    df: pd.DataFrame,
    palette: dict[str, str],
) -> tuple[Figure, Axes]:
    """Orchestrate 100% stacked horizontal bar chart rendering for authorship distribution
    with dynamic width scaling based on the actual saved image width.

    Args:
        df: DataFrame containing retraction authorship statistics by year.
        palette: Dictionary containing hex color strings.

    Returns:
        A tuple containing (Figure, Axes).
    """
    y_labels, df_pct, y_pos = prepare_chart_data(df)

    fig, ax = plt.subplots(figsize=(CHART_WIDTH, 4.50))
    fig.subplots_adjust(left=0.15, right=0.9, top=0.72, bottom=0)

    plot_stacked_horizontal_bars(ax=ax, y_pos=y_pos, df_pct=df_pct, palette=palette)
    add_percentage_labels(ax=ax, y_pos=y_pos, df_pct=df_pct)
    format_authorship_axes_and_spines(
        ax=ax,
        palette=palette,
        y_pos=y_pos,
        y_labels=y_labels,
    )

    file_path = "output/year-wise-pattern.png"
    fig.savefig(
        file_path,
        bbox_inches="tight",
    )

    with Image.open(file_path) as image:
        actual_image_width, _ = image.size

    fig.canvas.draw()
    plot_area_width = int(ax.get_window_extent().width)

    if plot_area_width > 0:
        non_plot_width = actual_image_width - plot_area_width
        target_plot_width = TARGET_IMAGE_WIDTH - non_plot_width
        new_chart_width = CHART_WIDTH * (
            target_plot_width / plot_area_width
        )
        fig.set_size_inches(new_chart_width, 4.50)
        fig.canvas.draw()

    with Image.open(file_path) as image:
        actual_image_width, _ = image.size

    return fig, ax

print("Done")