from src.analytics.clustering import fit_review_clusters, write_cluster_artifacts


def _synthetic_records():
    food_terms = "delicious tasty biryani food fresh flavor" * 3
    service_terms = "rude staff slow waiter service delay wait" * 3
    records = []
    for i in range(6):
        records.append({"review_id": f"f{i}", "branch_id": "branch_a", "review_date": "2026-01-01T00:00:00+00:00", "cleaned_text": food_terms})
    for i in range(6):
        records.append({"review_id": f"s{i}", "branch_id": "branch_b", "review_date": "2026-01-02T00:00:00+00:00", "cleaned_text": service_terms})
    return records


def test_fit_review_clusters_selects_k_and_assigns_documents():
    result = fit_review_clusters(_synthetic_records(), k_candidates=range(2, 4), min_df=1, max_df=1.0)

    assert result["method"] == "tfidf_kmeans_v1"
    assert result["params"]["selected_k"] in (2, 3)
    assert len(result["document_clusters"]) == 12
    assert len(result["clusters"]) == result["params"]["selected_k"]
    assert -1.0 <= result["selected_silhouette_score"] <= 1.0


def test_fit_review_clusters_raises_when_too_few_documents():
    try:
        fit_review_clusters([{"cleaned_text": "great food"}], min_df=5)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_write_cluster_artifacts_creates_files(tmp_path):
    result = fit_review_clusters(_synthetic_records(), k_candidates=range(2, 4), min_df=1, max_df=1.0)

    write_cluster_artifacts(result, tmp_path)

    assert (tmp_path / "cluster_model_kmeans.json").exists()
    assert (tmp_path / "review_clusters_kmeans.csv").exists()
