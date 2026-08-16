import pandas as pd

from app.display import business_dataframe


def test_business_dataframe_removes_duplicate_manager_column_names():
    source = pd.DataFrame(
        [
            {
                "branch_name": "Banjara Hills",
                "branch_id": "banjara_hills",
                "month": "2026-08",
                "review_count": 25,
            }
        ]
    )

    display = business_dataframe(source)

    assert list(display.columns) == ["branch", "month", "reviews"]
    assert display["branch"].iloc[0] == "Banjara Hills"
