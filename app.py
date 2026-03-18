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
# Eventos (Dados inalterados)
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

col1, col2 = st.columns([2, 1])

def get_style(tipo):
    if tipo == "DUEL LOST": return 'x', (1, 0, 0, 0.8), 120, 2.5
    elif tipo == "DUEL WON": return 'o', (0, 0.6, 0, 0.9), 120, 0.5
    elif tipo == "AERIAL WON": return '^', (0.2, 0.3, 1, 0.9), 140, 0.5
    elif tipo == "FOULED": return 's', (1, 0.6, 0, 0.9), 120, 0.5
    elif tipo == "INTERCEPTION": return 'D', (0.3, 0.3, 0.3, 0.9), 120, 0.5

with col1:
    # 1. Criar o Pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f5f5f5', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # IMPORTANTE: Fixar as margens para que o ax não "flutue"
    # Isso garante que sabemos exatamente onde o campo está na imagem salva.
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)

    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["tipo"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=color, linewidths=lw, ax=ax)

    ax.set_title("Defensive & Duel Map", fontsize=18)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Duel Won', markerfacecolor=(0, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='x', color=(1, 0, 0, 0.8), label='Duel Lost', markersize=10, linewidth=2),
        Line2D([0], [0], marker='^', color='w', label='Aerial Won', markerfacecolor=(0.2, 0.3, 1, 0.9), markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Fouled', markerfacecolor=(1, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='D', color='w', label='Interception', markerfacecolor=(0.3, 0.3, 0.3, 0.9), markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True)

    # 2. Obter a posição do AXIS dentro da FIGURA (em escala 0 a 1)
    bbox = ax.get_position() # [x0, y0, width, height]
    
    # 3. Salvar a imagem SEM o bbox_inches='tight' 
    # (O 'tight' é o que quebra a sua lógica, pois ele corta as bordas de forma imprevisível)
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100) 
    buf.seek(0)
    image = Image.open(buf)

    # Exibir imagem e capturar clique
    click = streamlit_image_coordinates(image, use_column_width=True)

# ==========================
# Lógica de mapeamento Precisa
# ==========================
selected_event = None

if click is not None:
    img_w, img_h = image.size
    
    # Coordenadas do clique normalizadas (0 a 1) em relação à imagem total
    click_x_norm = click["x"] / img_w
    click_y_norm = click["y"] / img_h

    # Mapear o clique para dentro da área do AX (o campo)
    # Statsbomb X: 0 (esquerda) a 120 (direita)
    # Statsbomb Y: 0 (cima) a 80 (baixo)
    
    # Cálculo para X:
    field_x = ((click_x_norm - bbox.x0) / bbox.width) * 120
    
    # Cálculo para Y (Matplotlib inverte o eixo Y em relação ao clique da imagem):
    # O topo do campo no Statsbomb é 0. Na imagem, o topo é 0.
    # Mas o bbox.y0 conta de baixo para cima.
    field_y = ((click_y_norm - (1 - bbox.y1)) / bbox.height) * 80

    # Filtro de segurança: verificar se o clique foi dentro do campo
    if 0 <= field_x <= 120 and 0 <= field_y <= 80:
        df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
        
        # Raio de busca (ajustável)
        RADIUS = 4 
        candidates = df[df["dist"] < RADIUS]

        if not candidates.empty:
            selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Exibição do Vídeo
# ==========================
with col2:
    st.subheader("Análise de Vídeo")
    if selected_event is not None:
        st.success(f"Evento Selecionado: {selected_event['tipo']}")
        st.info(f"Coordenadas Campo: ({selected_event['x']:.1f}, {selected_event['y']:.1f})")
        try:
            st.video(selected_event["video"])
        except:
            st.error("Vídeo não encontrado no caminho especificado.")
    else:
        st.write("Clique em um ícone no mapa para carregar o vídeo correspondente.")
        st.caption("Dica: Tente clicar exatamente no centro do ícone.")
