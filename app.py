import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

st.set_page_config(layout="wide")

st.title("Defensive & Duel Map")

# ==========================
# Eventos + vídeos
# ==========================
eventos = [
    ("FOULED", 89.09, 12.07, "videos/Fouled 1.mp4"),
    ("DUEL LOST", 101.23, 22.05, "videos/Duel Lost 0.mp4"),
    ("DUEL WON", 65.82, 69.09, "videos/Duel Won 1.mp4"),
    ("DUEL WON", 69.14, 25.87, "videos/Duel Won 2.mp4"),
    ("DUEL LOST", 26.75, 10.41, "videos/Duel Lost 1.mp4"),
    ("AERIAL WON", 76.62, 27.53, "videos/Aeriel Won 1.mp4"),
    ("DUEL LOST", 109.04, 69.09, "videos/Duel Lost 2.mp4"),
    ("DUEL LOST", 85.93, 36.68, "videos/Duel Lost 3.mp4"),
    ("DUEL LOST", 76.12, 30.69, "videos/Duel Lost 4.mp4"),
    ("FOULED", 52.35, 55.63, "videos/Fouled 2.mp4"),
    ("DUEL LOST", 56.34, 49.14, "videos/Duel Lost 6.mp4"),
    ("INTERCEPTION", 64.16, 20.38, "videos/Interception.mp4"),
]

df = pd.DataFrame(eventos, columns=["tipo", "x", "y", "video"])

# ==========================
# Layout
# ==========================
col1, col2 = st.columns([2, 1])

# ==========================
# Função para estilo
# ==========================
def get_style(tipo):
    if tipo == "DUEL LOST":
        return 'x', (1, 0, 0, 0.8), 120, 2.5
    elif tipo == "DUEL WON":
        return 'o', (0, 0.6, 0, 0.9), 120, 0.5
    elif tipo == "AERIAL WON":
        return '^', (0.2, 0.3, 1, 0.9), 140, 0.5
    elif tipo == "FOULED":
        return 's', (1, 0.6, 0, 0.9), 120, 0.5
    elif tipo == "INTERCEPTION":
        return 'D', (0.3, 0.3, 0.3, 0.9), 120, 0.5

# ==========================
# Mapa como imagem clicável
# ==========================
with col1:
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#f5f5f5',
        line_color='#4a4a4a'
    )

    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_dpi(100) # Fixando a densidade de pixels

    # Plot eventos
    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["tipo"])
        pitch.scatter(
            row.x, row.y, marker=marker, s=size, color=color,
            edgecolors=color, linewidths=lw, ax=ax
        )

    ax.set_title("Defensive & Duel Map")

    # Legenda
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Duel Won', markerfacecolor=(0, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='x', color=(1, 0, 0, 0.8), label='Duel Lost', markersize=10, linewidth=2),
        Line2D([0], [0], marker='^', color='w', label='Aerial Won', markerfacecolor=(0.2, 0.3, 1, 0.9), markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Fouled', markerfacecolor=(1, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='D', color='w', label='Interception', markerfacecolor=(0.3, 0.3, 0.3, 0.9), markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', edgecolor='black', framealpha=1)

    # Salvar imagem
    buf = BytesIO()
    plt.savefig(buf, format="png") # Sem bbox_inches para manter a proporção exata da figura
    buf.seek(0)
    image = Image.open(buf)

    # === A MÁGICA ACONTECE AQUI ===
    # 1. Pegamos as coordenadas extremas do campo do StatsBomb (0,0 até 120,80)
    corners_data = np.array([[0, 0], [120, 80]]) 
    
    # 2. Descobrimos exatamente em quais pixels da imagem esses cantos foram desenhados
    corners_display = ax.transData.transform(corners_data)
    fig_h = fig.get_figheight() * fig.dpi
    
    px_left = corners_display[0, 0]
    px_top = fig_h - corners_display[0, 1]
    px_right = corners_display[1, 0]
    px_bottom = fig_h - corners_display[1, 1]
    # ===============================

    # use_column_width=True ajusta o visual no Streamlit sem quebrar a proporção do clique
    click = streamlit_image_coordinates(image, use_column_width=True)

# ==========================
# Detectar evento clicado
# ==========================
selected_event = None

if click is not None:
    x_click = click["x"]
    y_click = click["y"]

    # Transformamos o clique em uma porcentagem (0.0 a 1.0) dentro do retângulo do campo
    ratio_x = (x_click - px_left) / (px_right - px_left)
    ratio_y = (y_click - px_top) / (px_bottom - px_top)

    # Multiplicamos a porcentagem pelas dimensões totais do StatsBomb (120x80)
    field_x = ratio_x * 120
    field_y = ratio_y * 80

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)

    RADIUS = 6 # Aumentei levemente a área de clique para melhorar a experiência do usuário

    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Vídeo
# ==========================
with col2:
    st.subheader("Event Video")

    if selected_event is not None:
        st.write(f"**Type:** {selected_event['tipo']}")
        try:
            st.video(selected_event["video"])
        except:
            st.warning("Video file not found.")
    else:
        st.info("Click on a map event to watch.")
