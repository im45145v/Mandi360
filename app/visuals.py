"""Small, reusable visual helpers for the Streamlit presentation layer."""
from __future__ import annotations

from collections.abc import Iterable

import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import STOPWORDS, WordCloud


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

    cloud = WordCloud(
        width=900,
        height=450,
        background_color="#FFF8E7",
        colormap=color_map,
        stopwords=STOPWORDS,
        collocations=False,
        min_font_size=12,
        max_words=80,
        random_state=42,
    ).generate(content)
    figure, axis = plt.subplots(figsize=(10, 4.8))
    axis.imshow(cloud, interpolation="bilinear")
    axis.axis("off")
    axis.set_title(title, fontsize=14, color="#3B0A0A", pad=12)
    figure.patch.set_facecolor("#FFF8E7")
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)