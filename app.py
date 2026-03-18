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

    # Plot eventos
    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["tipo"])

        pitch.scatter(
            row.x,
            row.y,
            marker=marker,
            s=size,
            color=color,
            edgecolors=color,
            linewidths=lw,
            ax=ax
        )

    ax.set_title("Defensive & Duel Map")

    # ==========================
    # Legenda (posição correta)
    # ==========================
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Duel Won',
               markerfacecolor=(0, 0.6, 0, 0.9), markersize=10),

        Line2D([0], [0], marker='x', color=(1, 0, 0, 0.8), label='Duel Lost',
               markersize=10, linewidth=2),

        Line2D([0], [0], marker='^', color='w', label='Aerial Won',
               markerfacecolor=(0.2, 0.3, 1, 0.9), markersize=10),

        Line2D([0], [0], marker='s', color='w', label='Fouled',
               markerfacecolor=(1, 0.6, 0, 0.9), markersize=10),

        Line2D([0], [0], marker='D', color='w', label='Interception',
               markerfacecolor=(0.3, 0.3, 0.3, 0.9), markersize=10),
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper left',
        frameon=True,
        facecolor='white',
        edgecolor='black',
        framealpha=1
    )

    # Salvar imagem com legenda
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.3)
    buf.seek(0)

    image = Image.open(buf)

    click = streamlit_image_coordinates(image)

# ==========================
# Detectar evento clicado
# ==========================
selected_event = None

if click is not None:
    click_x = click["x"]
    click_y = click["y"]

    img_w, img_h = image.size

    field_x = click_x * (120 / img_w)
    field_y = click_y * (80 / img_h)

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)

    RADIUS = 5

    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]
    else:
        selected_event = None

# ==========================
# Vídeo
# ==========================
with col2:
    st.subheader("Event")

    if selected_event is not None:
        st.write(f"**Type:** {selected_event['tipo']}")
        try:
            st.video(selected_event["video"])
        except:
            st.warning("Not found.")
    else:
        st.info("Click on the event to watch.")
