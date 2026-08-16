from src.analytics.topics import fit_topic_model, write_topic_artifacts


def _synthetic_records():
    food_terms = "delicious tasty biryani food fresh flavor" * 3
    service_terms = "rude staff slow waiter service delay wait" * 3
    records = []
    for i in range(6):
        records.append(
            {
                "review_id": f"f{i}",
                "branch_id": "branch_a",
                "review_date": "2026-01-01T00:00:00+00:00",
                "cleaned_text": food_terms,
            }
        )
    for i in range(6):
        records.append(
            {
                "review_id": f"s{i}",
                "branch_id": "branch_b",
                "review_date": "2026-01-02T00:00:00+00:00",
                "cleaned_text": service_terms,
            }
        )
    return records


def test_fit_topic_model_returns_topics_and_document_assignments():
    model = fit_topic_model(_synthetic_records(), num_topics=2, min_df=1, max_df=1.0)

    assert model["method"] == "tfidf_nmf_v1"
    assert model["status"] == "derived_ml_unvalidated"
    assert model["params"]["num_topics_fitted"] == 2
    assert len(model["topics"]) == 2
    assert all(len(topic["top_terms"]) > 0 for topic in model["topics"])
    assert len(model["document_topics"]) == 12
    assert all("dominant_topic" in row for row in model["document_topics"])


def test_fit_topic_model_raises_when_too_few_documents():
    try:
        fit_topic_model([{"cleaned_text": "great food"}], min_df=5)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_write_topic_artifacts_creates_files(tmp_path):
    model = fit_topic_model(_synthetic_records(), num_topics=2, min_df=1, max_df=1.0)

    write_topic_artifacts(model, tmp_path)

    assert (tmp_path / "topic_model_nmf.json").exists()
    assert (tmp_path / "review_topics_nmf.csv").exists()
