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

def render_retraction_subject_chart(
    df: pd.DataFrame,
    palette: dict[str, str]
) -> tuple[Figure, Axes]:
    """Orchestrate structured stacked horizontal bar chart with top column headers

    (SUBJECT, TOTAL, WITHOUT 2023 | 2023), absolute value labels, and dynamic width fixing.

    Args:
        df: DataFrame containing combined subject retraction metrics.
        palette: Dictionary containing hex color strings.
        dpi: Figure resolution.

    Returns:
        A tuple containing (Figure, Axes).
    """
    # Lấy top 5 và đảo chiều để item lớn nhất nằm ở vị trí y cao nhất (trên cùng)
    df_plot = df.iloc[::-1].reset_index(drop=True)
    y_labels = df_plot["subject"].tolist()
    total_vals = df_plot["total_count"].tolist()
    without_vals = df_plot["count_excluding_2023"].tolist()
    count_2023_vals = df_plot["count_2023"].tolist()
    y_pos = np.arange(len(y_labels))

    max_val = max(total_vals, default=10)
    step = 10
    x_upper_limit = int((max_val // step + 1) * step)

    fig, ax = plt.subplots(figsize=(CHART_WIDTH, 2.50))
    fig.subplots_adjust(left=0.02, right=1, top=1, bottom=0)

    x_min = -max_val * 0.15
    x_max = x_upper_limit
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.8, len(y_labels) - 0.2)

    n = len(total_vals)
    highlighted_visual_positions = {1, 2, 3}
    highlighted_indices = {
        n - pos for pos in highlighted_visual_positions if 0 <= n - pos < n
    }

    colors_without = [
        palette["blue_primary"] if i in highlighted_indices else palette["GRAY_DARK"]
        for i in range(n)
    ]
    colors_2023 = [
        palette["blue_lighter"] if i in highlighted_indices else palette["gray_light"]
        for i in range(n)
    ]

    ax.barh(y_pos, without_vals, left=0, color=colors_without, height=0.8)
    ax.barh(y_pos, count_2023_vals, left=without_vals, color=colors_2023, height=0.8)

    x_total_pos = -max_val * 0.085
    for i, (t_val, y) in enumerate(zip(total_vals, y_pos)):
        is_highlighted = i in highlighted_indices
        text_color = palette["blue_primary"] if is_highlighted else palette["GRAY_DARK"]
        font_weight = "bold" if is_highlighted else "normal"
        # 1. Hiển thị giá trị cột TOTAL
        ax.annotate(
            text=f"{t_val:,}",
            xy=(x_total_pos, y),
            xytext=(0, -1),  # Dịch xuống 2 points để thẳng hàng hoàn hảo với nhãn Y
            textcoords="offset points",
            ha="center",
            va="center",
            color=text_color,
            fontsize=DEFAULT_FONT_SIZE,
            fontweight=font_weight,
        )

        # 2. Hiển thị giá trị phân khúc without 2023 bên trong bar
        w_val = without_vals[i]
        if w_val > 0:
            ax.annotate(
                text=f"{w_val:,}",
                xy=(0, y),
                xytext=(5, -1),  # Cách mép trái của bar 6 points
                textcoords="offset points",
                ha="left",
                va="center",
                color="white",
                fontsize=ANNOTATION_FONT_SIZE,
                fontweight="normal",
            )

        # 3. Hiển thị giá trị phân khúc 2023 bên trong bar
        c_val = count_2023_vals[i]
        if c_val > 0:
            ax.annotate(
                text=f"{c_val:,}",
                xy=(t_val, y),
                xytext=(-5, -1),  # Cách mép trái của đoạn 2023 là 6 points
                textcoords="offset points",
                ha="right",
                va="center",
                color=palette["GRAY_DARK"],
                fontsize=ANNOTATION_FONT_SIZE,
                fontweight="normal",
            )

    # Cấu hình nhãn trục Y
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=DEFAULT_FONT_SIZE)

    for i, tick_label in enumerate(ax.get_yticklabels()):
        if i in highlighted_indices:
            tick_label.set_color(palette["blue_primary"])
            tick_label.set_fontweight("bold")
        else:
            tick_label.set_color(palette["GRAY_DARK"])

    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_ticks_position("none")

    # Tiêu đề các cột phía trên
    fig.text(0, 1, "SUBJECT", fontsize=FOOTNOTE_FONT_SIZE, color=palette["GRAY_DARK"], ha="right")
    fig.text(0.075, 1, "TOTAL", fontsize=FOOTNOTE_FONT_SIZE, color=palette["GRAY_DARK"], ha="center")
    fig.text(
    0.145,
    1,
    r"$\mathbf{Other}$ Years",
    fontsize=FOOTNOTE_FONT_SIZE,
    color=palette["GRAY_DARK"],
    ha="left",
)
    fig.text(0.325, 1.005, "|", fontsize=FOOTNOTE_FONT_SIZE, color=palette["GRAY_DARK"], ha="center")
    fig.text(
    0.335,
    1,
    r"$\mathbf{Peak}$ Year (2023)",
    fontsize=FOOTNOTE_FONT_SIZE,
    color=palette["gray_text"],
    ha="left",
)
    file_path = "output/top-5-subjects-ranking.png"
    fig.savefig(
        file_path,
        bbox_inches="tight",
    )

    with Image.open(file_path) as image:
        actual_image_width, _ = image.size

    fig.canvas.draw()
    plot_area_width = int(ax.get_window_extent().width)

    if plot_area_width > 0 and "TARGET_IMAGE_WIDTH" in globals():
        non_plot_width = actual_image_width - plot_area_width
        target_plot_width = TARGET_IMAGE_WIDTH - non_plot_width

        if plot_area_width > 0:
            new_chart_width = CHART_WIDTH * (
                target_plot_width / plot_area_width
            )

            fig.set_size_inches(new_chart_width, 2.50)
            fig.canvas.draw()

            # Lưu lại lần cuối với kích thước đã điều chỉnh chuẩn xác
            fig.savefig(
                file_path,
                bbox_inches="tight",
            )

    return fig, ax