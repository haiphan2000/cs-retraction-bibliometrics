import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image
from src.plotting_styles import *
from src.utils import *
import textwrap

TARGET_IMAGE_WIDTH = 3353
CHART_WIDTH = 10

def build_cooccurrence_graph(df, min_weight=0.0002):
    """
    Xây dựng NetworkX Graph, lọc theo min_weight, 
    đồng thời lưu lại tần số (freq) của từng node.
    """
    G = nx.Graph()
    node_freqs = {}
    
    for _, row in df.iterrows():
        weight = row['weight']
        if weight >= min_weight:
            r_a, r_b = row['reason_a'], row['reason_b']
            f_a, f_b = row['freq_a'], row['freq_b']
            
            # Thêm cạnh với trọng số weight
            G.add_edge(r_a, r_b, weight=weight)
            
            # Lưu tần số tương ứng cho từng node
            node_freqs[r_a] = f_a
            node_freqs[r_b] = f_b
            
    # Xóa các nút bị cô lập sau khi lọc
    G.remove_nodes_from(list(nx.isolates(G)))
    return G, node_freqs

def plot_cooccurrence_network(df, model_name, palette, min_weight=0.0002, max_length=15):
    """
    Vẽ mạng đồng xuất hiện:
    - Node size: tính theo freq của chính nó (dùng sqrt scaling).
    - Edge weight: lấy từ cột weight trong df.
    """
    # 1. Tạo đồ thị và lấy từ điển tần số node
    G, node_freqs = build_cooccurrence_graph(df, min_weight=min_weight)
    
    if len(G.nodes()) == 0:
        print(f"Cảnh báo: Mô hình '{model_name}' không có nút nào để vẽ sau khi lọc.")
        return

    # 2. Thiết lập khung hình
    plt.figure(figsize=(10, 7))
    
    # Bố cục lò xo có kể đến trọng số cạnh (giúp các node liên kết chặt xích lại gần nhau)
    pos = nx.spring_layout(G, weight='weight', k=0.15, iterations=20)

    # 3. Tính toán độ dày cạnh dựa trên cột weight
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_w = max(weights) if weights else 1
    edge_widths = [0.8 + 3.5 * (w / max_w) for w in weights]

    # 4. Tính toán kích thước nút dựa trên freq (DÙNG SQRT NHƯ ĐÃ THỐNG NHẤT)
    filtered_freqs = [node_freqs.get(node, 1) for node in G.nodes()]
    max_freq = max(filtered_freqs) if filtered_freqs else 1
    
    node_sizes = []
    for node in G.nodes():
        freq = node_freqs.get(node, 1)
        # Áp dụng công thức căn bậc hai cho freq để cân bằng kích thước lớn/nhỏ
        scaled_size = 400
        node_sizes.append(scaled_size)

    # 5. Tự động xuống dòng nhãn theo max_length
    labels = {node: textwrap.fill(str(node), width=max_length) for node in G.nodes()}

    # 6. Trích xuất màu từ PALETTE
    node_color = palette["gray_light"]
    edge_color = palette["blue_primary"]
    text_color = palette["GRAY_DARK"]

    # 7. Vẽ các thành phần đồ thị
    #nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.35, edge_color=edge_color)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_color, alpha=0.85)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold', font_color=text_color)

    # 8. Trang trí biểu đồ
    plt.title(f"Co-occurrence Network (Freq Sqrt Scale): {model_name}", fontsize=16, fontweight='bold', color=text_color, pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.show()