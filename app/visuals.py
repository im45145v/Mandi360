"""Small, reusable visual helpers for the Streamlit presentation layer."""
from __future__ import annotations

from collections.abc import Iterable

import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import STOPWORDS, WordCloud

WORDCLOUD_PALETTES = {
    "positive": ["#0F6B72", "#147C66", "#2D7A3E", "#4B8B2D", "#A67C00"],
    "negative": ["#A6192E", "#7A1F2B", "#B23A2E", "#8C2F39", "#3B0A0A"],
    "neutral": ["#0F6B72", "#A6192E", "#C9A227", "#134E4A", "#7A1F2B"],
}


def _palette_for(color_map: str) -> list[str]:
    lowered = color_map.lower()
    if "gn" in lowered:
        return WORDCLOUD_PALETTES["positive"]
    if "rd" in lowered or "or" in lowered:
        return WORDCLOUD_PALETTES["negative"]
    return WORDCLOUD_PALETTES["neutral"]


def show_wordcloud(
    texts: Iterable[object],
    title: str,
    color_map: str,
    empty_message: str = "Not enough review text is available for this view.",
) -> None:
    """Render a readable word cloud from review text, or a useful empty state."""
    content = " ".join(
        str(text)
        for text in texts
        if text is not None and str(text).strip() and str(text).lower() != "nan"
    )
    if not content:
        st.info(empty_message)
        return

    palette = _palette_for(color_map)

    def color_func(*args, **kwargs):
        word = args[0]
        return palette[sum(ord(char) for char in word) % len(palette)]

    cloud = WordCloud(
        width=900,
        height=450,
        background_color="white",
        color_func=color_func,
        stopwords=STOPWORDS,
        collocations=False,
        min_font_size=12,
        max_words=80,
        random_state=42,
        contour_width=1,
        contour_color="#E8DEC7",
    ).generate(content)
    figure, axis = plt.subplots(figsize=(10, 4.8))
    axis.imshow(cloud, interpolation="bilinear")
    axis.axis("off")
    axis.set_title(title, fontsize=14, color="#3B0A0A", pad=12)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)
