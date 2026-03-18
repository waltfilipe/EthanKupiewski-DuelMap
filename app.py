import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd

st.set_page_config(layout="wide")

st.title("Defensive & Duel Map")

# ==========================
# Eventos + vídeos
# ==========================
eventos = [
    ("FOULED", 89.09, 12.07, "videos/duelo_1.mp4"),
    ("DUEL LOST", 101.23, 22.05, "videos/duelo_2.mp4"),
    ("DUEL WON", 65.82, 69.09, "videos/duelo_3.mp4"),
    ("DUEL WON", 69.14, 25.87, "videos/duelo_4.mp4"),
    ("DUEL LOST", 26.75, 10.41, "videos/duelo_5.mp4"),
    ("AERIAL WON", 76.62, 27.53, "videos/duelo_6.mp4"),
    ("DUEL LOST", 109.04, 69.09, "videos/duelo_7.mp4"),
    ("DUEL LOST", 85.93, 36.68, "videos/duelo_8.mp4"),
    ("DUEL LOST", 76.12, 30.69, "videos/duelo_9.mp4"),
    ("FOULED", 52.35, 55.63, "videos/duelo_10.mp4"),
    ("DUEL LOST", 56.34, 49.14, "videos/duelo_11.mp4"),
    ("INTERCEPTION", 64.16, 20.38, "videos/duelo_12.mp4"),
]

df = pd.DataFrame(eventos, columns=["tipo", "x", "y", "video"])

# ==========================
# Layout (mapa + vídeo)
# ==========================
col1, col2 = st.columns([2, 1])

# ==========================
# Mapa
# ==========================
with col1:
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#f5f5f5',
        line_color='#4a4a4a'
    )

    fig, ax = pitch.draw(figsize=(10, 7))

    for i, row in df.iterrows():

        if row["tipo"] == "DUEL LOST":
            marker = 'x'
            color = (1, 0, 0, 0.8)
            size = 120
            lw = 2.5

        elif row["tipo"] == "DUEL WON":
            marker = 'o'
            color = (0, 0.6, 0, 0.9)
            size = 120
            lw = 0.5

        elif row["tipo"] == "AERIAL WON":
            marker = '^'
            color = (0.2, 0.3, 1, 0.9)
            size = 140
            lw = 0.5

        elif row["tipo"] == "FOULED":
            marker = 's'
            color = (1, 0.6, 0, 0.9)
            size = 120
            lw = 0.5

        elif row["tipo"] == "INTERCEPTION":
            marker = 'D'
            color = (0.3, 0.3, 0.3, 0.9)
            size = 120
            lw = 0.5

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

        # NUMERAÇÃO (importante para selecionar depois)
        ax.text(row.x, row.y, str(i),
                ha='center', va='center',
                fontsize=8, color='white')

    # legenda
    ax.scatter([], [], marker='o', color='green', label='Duel Won')
    ax.scatter([], [], marker='x', color='red', label='Duel Lost')
    ax.scatter([], [], marker='^', color='blue', label='Aerial Won')
    ax.scatter([], [], marker='s', color='orange', label='Fouled')
    ax.scatter([], [], marker='D', color='gray', label='Interception')

    ax.legend(
        loc='upper left',
        framealpha=1.0,
        facecolor='white',
        edgecolor='black'
    )

    plt.title("Defensive & Duel Map", fontsize=14)

    st.pyplot(fig)

# ==========================
# Seleção + vídeo
# ==========================
with col2:
    st.subheader("Selecionar evento")

    evento_selecionado = st.selectbox(
        "Escolha o duelo:",
        df.index,
        format_func=lambda x: f"{x} - {df.loc[x, 'tipo']}"
    )

    linha = df.loc[evento_selecionado]

    st.write(f"**Tipo:** {linha['tipo']}")
    st.write(f"**Coordenadas:** ({linha['x']:.1f}, {linha['y']:.1f})")

    # ==========================
    # Vídeo
    # ==========================
    try:
        st.video(linha["video"])
    except:
        st.warning("Vídeo não encontrado.")
