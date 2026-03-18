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

col1, col2 = st.columns([2, 1])

def get_style(event_type):
    if event_type == "DUEL LOST": return 'x', (1, 0, 0, 0.8), 120, 2.5
    elif event_type == "DUEL WON": return 'o', (0, 0.6, 0, 0.9), 120, 0.5
    elif event_type == "AERIAL WON": return '^', (0.2, 0.3, 1, 0.9), 140, 0.5
    elif event_type == "FOULED": return 's', (1, 0.6, 0, 0.9), 120, 0.5
    elif event_type == "INTERCEPTION": return 'D', (0.3, 0.3, 0.3, 0.9), 120, 0.5

# ==========================
# Map Visualization (Left Col)
# ==========================
with col1:
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f5f5f5', line_color='#4a4a4a')
    # Increased figsize slightly to accommodate the arrow at the bottom
    fig, ax = pitch.draw(figsize=(10, 8))
    
    # Plot events
    for _, row in df.iterrows():
        marker, color, size, lw = get_style(row["type"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=color, linewidths=lw, ax=ax)

    # Cleaned Title
    ax.set_title("Defensive & Duel Analysis", fontsize=18, pad=20)

    # --- Attack Direction Arrow ---
    # We place it just below the field (Y > 80 in StatsBomb coordinates)
    ax.annotate('', xy=(80, 84), xytext=(40, 84),
                arrowprops=dict(arrowstyle='->', color='#4a4a4a', lw=2))
    ax.text(60, 87, "Direction of Attack", ha='center', va='center', 
            fontsize=10, color='#4a4a4a', fontweight='bold')

    # Legend setup
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Duel Won', markerfacecolor=(0, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='x', color=(1, 0, 0, 0.8), label='Duel Lost', markersize=10, linewidth=2),
        Line2D([0], [0], marker='^', color='w', label='Aerial Won', markerfacecolor=(0.2, 0.3, 1, 0.9), markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Fouled', markerfacecolor=(1, 0.6, 0, 0.9), markersize=10),
        Line2D([0], [0], marker='D', color='w', label='Interception', markerfacecolor=(0.3, 0.3, 0.3, 0.9), markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True)

    # Convert plot to image
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    buf.seek(0)
    image = Image.open(buf)

    # Capture click
    click = streamlit_image_coordinates(image, use_column_width=True)

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
    
    # Precise conversion using axes transformation
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Nearest neighbor search
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    RADIUS = 4 
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
        st.info("Click on any marker on the map to play the video.")
