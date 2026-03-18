import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(layout="wide")

st.title("Defensive & Duel Map")

# ==========================
# Events + videos
# ==========================
events = [
    ("FOULED", 89.09, 12.07, "videos/fouled_1.mp4"),
    ("DUEL LOST", 101.23, 22.05, "videos/duel_lost_0.mp4"),
    ("DUEL WON", 65.82, 69.09, "videos/duel_won_1.mp4"),
    ("DUEL WON", 69.14, 25.87, "videos/duel_won_2.mp4"),
    ("DUEL LOST", 26.75, 10.41, "videos/duel_lost_1.mp4"),
    ("AERIAL WON", 76.62, 27.53, "videos/aerial_won_1.mp4"),
    ("DUEL LOST", 109.04, 69.09, "videos/duel_lost_2.mp4"),
    ("DUEL LOST", 85.93, 36.68, "videos/duel_lost_3.mp4"),
    ("DUEL LOST", 76.12, 30.69, "videos/duel_lost_4.mp4"),
    ("FOULED", 52.35, 55.63, "videos/fouled_2.mp4"),
    ("DUEL LOST", 56.34, 49.14, "videos/duel_lost_6.mp4"),
    ("INTERCEPTION", 64.16, 20.38, "videos/interception.mp4"),
]

df = pd.DataFrame(events, columns=["type", "x", "y", "video"])

# ==========================
# Style function
# ==========================
def get_style(event_type):
    if event_type == "DUEL LOST":
        return 'x', (1, 0, 0, 0.8), 120, 2.5
    elif event_type == "DUEL WON":
        return 'o', (0, 0.6, 0, 0.9), 120, 0.5
    elif event_type == "AERIAL WON":
        return '^', (0.2, 0.3, 1, 0.9), 140, 0.5
    elif event_type == "FOULED":
        return 's', (1, 0.6, 0, 0.9), 120, 0.5
    elif event_type == "INTERCEPTION":
        return 'D', (0.3, 0.3, 0.3, 0.9), 120, 0.5

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
    marker, color, size, lw = get_style(row["type"])

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

ax.set_title("Click on an event to watch the video")

# ==========================
# Convert to image (fix)
# ==========================
buf = BytesIO()
plt.savefig(buf, format="png", bbox_inches='tight')
buf.seek(0)

image = Image.open(buf)

# ==========================
# Clickable image
# ==========================
click = streamlit_image_coordinates(image)

st.image(image, use_container_width=True)

# ==========================
# Detect clicked event
# ==========================
selected_event = None

if click is not None:
    click_x = click["x"]
    click_y = click["y"]

    # scale conversion (may need slight tuning)
    field_x = click_x * (120 / image.size[0])
    field_y = click_y * (80 / image.size[1])

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    selected_event = df.loc[df["dist"].idxmin()]

# ==========================
# Video section (BOTTOM)
# ==========================
st.markdown("---")

if selected_event is not None:
    st.subheader(f"Event: {selected_event['type']}")
    st.write(f"Location: ({selected_event['x']:.1f}, {selected_event['y']:.1f})")

    st.video(selected_event["video"])
else:
    st.info("Click on any event on the pitch to display the video.")
