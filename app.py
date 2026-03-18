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

# Dados originais
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
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f5f5f5', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Plotagem
    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["tipo"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, edgecolors=color, linewidths=lw, ax=ax)

    ax.set_title("Defensive & Duel Map (X=0 Defesa | X=120 Ataque)", fontsize=15)

    # Salvar para imagem
    buf = BytesIO()
    # dpi=100 facilita a conta de conversão
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    image = Image.open(buf)

    # Captura o clique considerando o redimensionamento da coluna
    click = streamlit_image_coordinates(image, use_column_width=True)

# ==========================
# Lógica de Mapeamento Milimétrica
# ==========================
selected_event = None

if click is not None:
    # 1. Tamanho real da imagem salva (em pixels)
    real_w, real_h = image.size
    
    # 2. Tamanho da imagem exibida no navegador (em pixels)
    disp_w, disp_h = click["width"], click["height"]
    
    # 3. Escalar o clique para o tamanho real da imagem
    scale_x = real_w / disp_w
    scale_y = real_h / disp_h
    
    pixel_x = click["x"] * scale_x
    pixel_y = click["y"] * scale_y
    
    # 4. Inverter o Y (Matplotlib: 0 é embaixo | Imagem: 0 é em cima)
    mpl_pixel_y = real_h - pixel_y
    
    # 5. Transformar pixel real em coordenada do campo (StatsBomb)
    # O transformador transData.inverted() ignora margens, legendas e títulos automaticamente
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Cálculo da distância para achar o evento
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Raio de busca (4 unidades StatsBomb é um tamanho bom)
    RADIUS = 4 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Saída de Vídeo e Debug
# ==========================
with col2:
    st.subheader("Painel de Evento")
    if selected_event is not None:
        st.success(f"**Evento:** {selected_event['tipo']}")
        st.write(f"📍 **Coordenadas Reais:** ({selected_event['x']}, {selected_event['y']})")
        
        try:
            st.video(selected_event["video"])
        except:
            st.error("Arquivo de vídeo não encontrado.")
    else:
        st.info("Clique em um marcador no mapa.")
        if click:
            st.warning(f"Você clicou em ({field_x:.1f}, {field_y:.1f}), mas não há eventos aqui.")
