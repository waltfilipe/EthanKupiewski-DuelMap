import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")

st.title("Defensive & Duel Map")

# ==========================
# Events + videos
# ==========================
events = [
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

df = pd.DataFrame(events, columns=["type", "x", "y", "video"])

# ==========================
# Style + radius (KEY FIX)
# ==========================
def get_style(event_type):
    if event_type == "DUEL LOST":
        return 'x', (1, 0, 0, 0.8), 120, 2.5, 3.5
    elif event_type == "DUEL WON":
        return 'o', (0, 0.6, 0, 0.9), 120, 0.5, 3.5
    elif event_type == "AERIAL WON":
        return '^', (0.2, 0.3, 1, 0.9), 140, 0.5, 4.5  # MAIOR ÁREA
    elif event_type == "FOULED":
        return 's', (1, 0.6, 0, 0.9), 120, 0.5, 3.5
    elif event_type == "INTERCEPTION":
        return 'D', (0.3, 0.3, 0.3, 0.9), 120, 0.5, 3.5

# ==========================
# Pitch
# ==========================
pitch = Pitch(
    pitch_type='statsbomb',
    pitch_color='#f5f5f5',
    line_color='#4a4a4a'
)

fig, ax = pitch.draw(figsize=(10, 7))

for _, row in df.iterrows():
    marker, color, size, lw, _ = get_style(row["type"])

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

ax.set_title("Click on an event")

# ==========================
# Convert image
# ==========================
buf = BytesIO()
plt.savefig(buf, format="png", bbox_inches='tight')
buf.seek(0)

image = Image.open(buf)

# CLICK
click = streamlit_image_coordinates(image)

st.image(image, use_container_width=True)

# ==========================
# Click detection (FIXED)
# ==========================
selected_event = None

if click is not None:
    click_x = click["x"]
    click_y = click["y"]

    # conversão REAL (sem hardcode)
    img_w, img_h = image.size

    field_x = click_x * (120 / img_w)
    field_y = click_y * (80 / img_h)

    candidates = []

    for i, row in df.iterrows():
        _, _, _, _, radius = get_style(row["type"])

        dist = np.sqrt((row["x"] - field_x)**2 + (row["y"] - field_y)**2)

        if dist < radius:
            candidates.append((i, dist, row["type"]))

    if len(candidates) > 0:
        # prioridade (AERIAL primeiro)
        priority = {
            "AERIAL WON": 1,
            "DUEL WON": 2,
            "DUEL LOST": 3,
            "FOULED": 4,
            "INTERCEPTION": 5
        }

        candidates = sorted(
            candidates,
            key=lambda x: (x[1], priority[x[2]])
        )

        selected_event = df.loc[candidates[0][0]]

# ==========================
# Video
# ==========================
st.markdown("---")

if selected_event is not None:
    st.subheader(f"Event: {selected_event['type']}")
    st.video(selected_event["video"])
else:
    st.info("Click on an event to watch the video.")
