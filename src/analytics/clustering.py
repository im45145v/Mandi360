"""Review clustering (TF-IDF + KMeans) with silhouette-based k selection.

Cluster ids are unlabeled groupings of similar reviews; only top terms per
cluster are reported, and no cluster is asserted to represent a specific
business meaning without human review.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

CLUSTER_METHOD = "tfidf_kmeans_v1"


def fit_review_clusters(
    records: Iterable[dict[str, Any]],
    k_candidates: Iterable[int] = range(2, 9),
    min_df: int = 5,
    max_df: float = 0.9,
    top_terms: int = 10,
    silhouette_sample_size: int = 2000,
    random_state: int = 42,
) -> dict[str, Any]:
    """Fit KMeans over TF-IDF review vectors, selecting k by sampled silhouette score.

    Raises ValueError if there are too few documents to cluster meaningfully.
    """
    rows = [record for record in records if record.get("cleaned_text")]
    if len(rows) < min_df:
        raise ValueError(f"Need at least {min_df} reviews with text to cluster, got {len(rows)}")

    corpus = [row["cleaned_text"] for row in rows]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=min_df, max_df=max_df)
    tfidf = vectorizer.fit_transform(corpus)
    terms = vectorizer.get_feature_names_out()

    candidates = [k for k in k_candidates if 2 <= k < tfidf.shape[0]]
    if not candidates:
        raise ValueError("No valid k candidates for the given dataset size")

    sample_size = min(silhouette_sample_size, tfidf.shape[0])
    diagnostics = []
    best = None
    for k in candidates:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = model.fit_predict(tfidf)
        score = silhouette_score(tfidf, labels, sample_size=sample_size, random_state=random_state)
        diagnostics.append({"k": k, "silhouette_score": round(float(score), 6)})
        if best is None or score > best["score"]:
            best = {"k": k, "score": score, "model": model, "labels": labels}

    cluster_terms = []
    centers = best["model"].cluster_centers_
    for cluster_idx, center in enumerate(centers):
        top_indices = center.argsort()[::-1][:top_terms]
        cluster_terms.append(
            {
                "cluster_id": cluster_idx,
                "size": int((best["labels"] == cluster_idx).sum()),
                "top_terms": [terms[i] for i in top_indices],
            }
        )

    document_clusters = [
        {
            "review_id": row.get("review_id"),
            "branch_id": row.get("branch_id"),
            "review_date": row.get("review_date"),
            "cluster_id": int(label),
        }
        for row, label in zip(rows, best["labels"])
    ]

    return {
        "method": CLUSTER_METHOD,
        "status": "derived_ml_unvalidated",
        "params": {
            "k_candidates": list(candidates),
            "selected_k": best["k"],
            "min_df": min_df,
            "max_df": max_df,
            "random_state": random_state,
            "documents_used": len(rows),
            "silhouette_sample_size": sample_size,
        },
        "silhouette_by_k": diagnostics,
        "selected_silhouette_score": round(float(best["score"]), 6),
        "clusters": cluster_terms,
        "document_clusters": document_clusters,
    }


def write_cluster_artifacts(cluster_model: dict[str, Any], output_dir: str | Path) -> None:
    """Write the fitted cluster model summary and per-review cluster assignments."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    document_clusters = cluster_model["document_clusters"]
    model_summary = {key: value for key, value in cluster_model.items() if key != "document_clusters"}
    (output / "cluster_model_kmeans.json").write_text(json.dumps(model_summary, indent=2), encoding="utf-8")

    doc_path = output / "review_clusters_kmeans.csv"
    if not document_clusters:
        doc_path.write_text("\n", encoding="utf-8")
        return
    with doc_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(document_clusters[0].keys()))
        writer.writeheader()
        writer.writerows(document_clusters)
