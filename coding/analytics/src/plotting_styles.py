import matplotlib.pyplot as plt
import seaborn as sns

PALETTE = {
    "black": "#000000",
    "GRAY_DARK": "#555655",
    "gray_text": "#646369",
    "gray_light_text": "#929497",
    "gray_light": "#D4D4D4",
    "gray_line": "#A6A6A5",
    "blue_primary": "#002060",
    "blue_light": "#80B1D3",
    "blue_lighter": "#c7d8eb",
    "white": "#FFFFFF",
}

ANNOTATION_FONT_SIZE = 13
DEFAULT_FONT_SIZE = 15
FOOTNOTE_FONT_SIZE = 11
HIGHLIGHTED_FONT_SIZE = 17

TEXT_WIDTH_MM = 210 - (25 * 2)
MM_TO_INCH = 25.4
#CHART_WIDTH = TEXT_WIDTH_MM / MM_TO_INCH

def setup_matplotlib_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"],
        "mathtext.fontset": "custom",
        "font.size": DEFAULT_FONT_SIZE,
        "mathtext.bf": "DejaVu Sans:bold",
        "mathtext.it": "DejaVu Sans:italic",
        "text.usetex": False,

        "figure.dpi": 400,
        "axes.edgecolor": PALETTE["GRAY_DARK"],
        "axes.linewidth": 1.25,
        "axes.labelcolor": PALETTE["GRAY_DARK"],
        "axes.labelsize": DEFAULT_FONT_SIZE,
        "axes.titlesize": DEFAULT_FONT_SIZE,

        "xtick.color": PALETTE["GRAY_DARK"],
        "xtick.labelcolor": PALETTE["GRAY_DARK"],
        "ytick.color": PALETTE["GRAY_DARK"],
        "ytick.labelcolor": PALETTE["GRAY_DARK"],
        "xtick.labelsize": DEFAULT_FONT_SIZE,
        "ytick.labelsize": DEFAULT_FONT_SIZE,

        "xtick.color": PALETTE["GRAY_DARK"],
        "ytick.color": PALETTE["GRAY_DARK"],
        "xtick.major.width": 1.25,
        "ytick.major.width": 1.25,
        "xtick.minor.width": 1.25,
        "ytick.minor.width": 1.25,
    })

setup_matplotlib_style()