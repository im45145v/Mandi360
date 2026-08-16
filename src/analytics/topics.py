"""Real topic modeling (TF-IDF + NMF) for cleaned review text.

Unlike the frequency-based topic candidates in analytics.nlp, this module fits
an actual unsupervised model (scikit-learn NMF) and reports the reconstruction
error as an honest fit-quality metric. Topic labels are NOT invented here:
each topic is described only by its top weighted terms, and downstream
consumers must treat topic numbers as unlabeled clusters of terms pending
human review.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

TOPIC_METHOD = "tfidf_nmf_v1"


def fit_topic_model(
    records: Iterable[dict[str, Any]],
    num_topics: int = 8,
    top_terms: int = 10,
    min_df: int = 5,
    max_df: float = 0.9,
    random_state: int = 42,
) -> dict[str, Any]:
    """Fit an NMF topic model over reviews with available cleaned text.

    Returns a dict with fitted topics (top terms/weights), per-document
    dominant-topic assignments, and the model's fit parameters/metrics.
    Raises ValueError if there are too few documents to fit meaningfully.
    """
    rows = [record for record in records if record.get("cleaned_text")]
    if len(rows) < min_df:
        raise ValueError(
            f"Need at least {min_df} reviews with text to fit a topic model, got {len(rows)}"
        )

    corpus = [row["cleaned_text"] for row in rows]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=min_df,
        max_df=max_df,
    )
    tfidf = vectorizer.fit_transform(corpus)
    terms = vectorizer.get_feature_names_out()

    effective_topics = min(num_topics, tfidf.shape[0], tfidf.shape[1])
    if effective_topics < 1:
        raise ValueError("Vocabulary is empty after filtering; cannot fit a topic model")

    model = NMF(n_components=effective_topics, init="nndsvd", random_state=random_state, max_iter=500)
    doc_topic = model.fit_transform(tfidf)

    topics = []
    for topic_idx, term_weights in enumerate(model.components_):
        top_indices = term_weights.argsort()[::-1][:top_terms]
        topics.append(
            {
                "topic_id": topic_idx,
                "top_terms": [terms[i] for i in top_indices],
                "top_term_weights": [round(float(term_weights[i]), 6) for i in top_indices],
            }
        )

    document_topics = []
    for row, weights in zip(rows, doc_topic):
        dominant_idx = int(weights.argmax())
        document_topics.append(
            {
                "review_id": row.get("review_id"),
                "branch_id": row.get("branch_id"),
                "review_date": row.get("review_date"),
                "dominant_topic": dominant_idx,
                "dominant_topic_weight": round(float(weights[dominant_idx]), 6),
            }
        )

    return {
        "method": TOPIC_METHOD,
        "status": "derived_ml_unvalidated",
        "params": {
            "num_topics_requested": num_topics,
            "num_topics_fitted": effective_topics,
            "min_df": min_df,
            "max_df": max_df,
            "random_state": random_state,
            "documents_used": len(rows),
            "vocabulary_size": len(terms),
        },
        "reconstruction_error": round(float(model.reconstruction_err_), 6),
        "topics": topics,
        "document_topics": document_topics,
    }


def write_topic_artifacts(topic_model: dict[str, Any], output_dir: str | Path) -> None:
    """Write the fitted topic model (terms/params/metrics) and per-review assignments."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    document_topics = topic_model["document_topics"]
    model_summary = {key: value for key, value in topic_model.items() if key != "document_topics"}
    (output / "topic_model_nmf.json").write_text(json.dumps(model_summary, indent=2), encoding="utf-8")

    import csv

    doc_path = output / "review_topics_nmf.csv"
    if not document_topics:
        doc_path.write_text("\n", encoding="utf-8")
        return
    with doc_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(document_topics[0].keys()))
        writer.writeheader()
        writer.writerows(document_topics)
