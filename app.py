import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# Page configuration
st.set_page_config(layout="wide", page_title="Defensive Analysis")

st.title("Defensive & Duel Map")

# ==========================
# Data Setup
# ==========================
events_data = [
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
df = pd.DataFrame(events_data, columns=["type", "x", "y", "video"])

# Changed column ratio to 1:1 for a more balanced look
col1, col2 = st.columns([1, 1])

def get_style(event_type):
    if event_type == "DUEL LOST": return 'x', (1, 0, 0, 0.8), 80, 2.0
    elif event_type == "DUEL WON": return 'o', (0, 0.6, 0, 0.9), 80, 0.5
    elif event_type == "AERIAL WON": return '^', (0.2, 0.3, 1, 0.9), 100, 0.5
    elif event_type == "FOULED": return 's', (1, 0.6, 0, 0.9), 80, 0.5
    elif event_type == "INTERCEPTION": return 'D', (0.3, 0.3, 0.3, 0.9), 80, 0.5

# ==========================
# Map Visualization (Left Col)
# ==========================
with col1:
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f5f5f5', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(6, 4.5)) # Smaller internal figure size
    
    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["type"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=color, linewidths=lw, ax=ax)

    ax.set_title("Defensive & Duel Analysis", fontsize=14, pad=10)

    # Attack Arrow
    ax.annotate('', xy=(70, 83), xytext=(50, 83),
                arrowprops=dict(arrowstyle='->', color='#4a4a4a', lw=1.2))
    ax.text(60, 86, "Attack Direction", ha='center', va='center', 
            fontsize=8, color='#4a4a4a', fontweight='bold')

    # Compact Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Won', markerfacecolor=(0, 0.6, 0, 0.9), markersize=6),
        Line2D([0], [0], marker='x', color=(1, 0, 0, 0.8), label='Lost', markersize=6, linewidth=1.5),
        Line2D([0], [0], marker='^', color='w', label='Aerial', markerfacecolor=(0.2, 0.3, 1, 0.9), markersize=6),
        Line2D([0], [0], marker='s', color='w', label='Fouled', markerfacecolor=(1, 0.6, 0, 0.9), markersize=6),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize='x-small', ncol=2)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    buf.seek(0)
    image = Image.open(buf)

    # KEY CHANGE: Removed use_column_width and set a fixed width of 500 pixels
    click = streamlit_image_coordinates(image, width=850)

# ==========================
# Coordinate Mapping Logic
# ==========================
selected_event = None

if click is not None:
    real_w, real_h = image.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    RADIUS = 5 # Slightly larger radius for easier clicking on smaller display
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video Player (Right Col)
# ==========================
with col2:
    st.subheader("Video Analysis")
    if selected_event is not None:
        st.success(f"**Selected:** {selected_event['type']}")
        try:
            st.video(selected_event["video"])
        except:
            st.error("Video file not found.")
    else:
        st.info("Click on a marker to play.")
