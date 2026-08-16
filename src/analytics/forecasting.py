"""Predictive analytics: monthly rating trend forecasting and branch risk scoring.

Uses a simple linear trend (scikit-learn LinearRegression) per branch on
monthly average rating, since the monthly history per branch is short and a
transparent linear extrapolation is more defensible than an opaque model on
this little data. Forecasts are explicitly labeled as predictions, not facts.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error

FORECAST_METHOD = "linear_trend_v1"


def _branch_series(monthly_features: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    series: dict[str, list[dict[str, Any]]] = {}
    for row in monthly_features:
        if row.get("average_rating") is None:
            continue
        series.setdefault(row["branch_id"], []).append(row)
    for rows in series.values():
        rows.sort(key=lambda row: row["month"])
    return series


def forecast_branch_ratings(
    monthly_features: Iterable[dict[str, Any]],
    horizon: int = 3,
    min_history: int = 6,
    holdout: int = 2,
) -> dict[str, Any]:
    """Fit a linear trend per branch on monthly average rating and forecast ahead.

    Branches with fewer than min_history months are skipped (reported, not forecasted).
    Evaluation metrics (MAE/RMSE/MAPE) are computed on a holdout of the most
    recent points actually observed, when there is enough history to do so.
    """
    series = _branch_series(monthly_features)
    branch_results = []
    skipped = []
    for branch_id, rows in sorted(series.items()):
        if len(rows) < min_history:
            skipped.append({"branch_id": branch_id, "months_available": len(rows)})
            continue

        x_all = [[i] for i in range(len(rows))]
        y_all = [row["average_rating"] for row in rows]

        evaluation = None
        if len(rows) - holdout >= 3:
            split = len(rows) - holdout
            model_eval = LinearRegression().fit(x_all[:split], y_all[:split])
            y_pred = model_eval.predict(x_all[split:])
            y_true = y_all[split:]
            naive_value = y_all[split - 1]
            naive_pred = [naive_value] * len(y_true)
            evaluation = {
                "holdout_size": holdout,
                "mae": round(float(mean_absolute_error(y_true, y_pred)), 6),
                "rmse": round(float(mean_squared_error(y_true, y_pred) ** 0.5), 6),
                "mape": round(float(mean_absolute_percentage_error(y_true, y_pred)), 6),
                "naive_mae": round(float(mean_absolute_error(y_true, naive_pred)), 6),
                "beats_naive_baseline": bool(
                    mean_absolute_error(y_true, y_pred) < mean_absolute_error(y_true, naive_pred)
                ),
            }

        model = LinearRegression().fit(x_all, y_all)
        future_x = [[len(rows) + step] for step in range(horizon)]
        forecast_values = model.predict(future_x)
        slope = float(model.coef_[0])
        residuals = [actual - predicted for actual, predicted in zip(y_all, model.predict(x_all))]
        residual_std = float((sum(value**2 for value in residuals) / max(len(residuals) - 2, 1)) ** 0.5)
        last_month = _parse_month(rows[-1]["month"])

        if slope <= -0.02:
            risk_level = "elevated"
        elif slope <= -0.005:
            risk_level = "watch"
        else:
            risk_level = "stable"

        branch_results.append(
            {
                "branch_id": branch_id,
                "months_available": len(rows),
                "trend_slope_per_month": round(slope, 6),
                "risk_level": risk_level,
                "evaluation": evaluation,
                "forecast": [
                    {
                        "step_ahead": step + 1,
                        "month": _add_months(last_month, step + 1),
                        "predicted_average_rating": round(_bounded_rating(float(value)), 4),
                        "lower_bound": round(_bounded_rating(float(value) - 1.96 * residual_std), 4),
                        "upper_bound": round(_bounded_rating(float(value) + 1.96 * residual_std), 4),
                    }
                    for step, value in enumerate(forecast_values)
                ],
            }
        )

    return {
        "method": FORECAST_METHOD,
        "status": "predicted_unvalidated",
        "params": {"horizon": horizon, "min_history_months": min_history, "holdout": holdout},
        "branches_forecasted": branch_results,
        "branches_skipped_insufficient_history": skipped,
    }


def _parse_month(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m")


def _add_months(value: datetime, offset: int) -> str:
    month_index = value.year * 12 + value.month - 1 + offset
    year, month_index = divmod(month_index, 12)
    return f"{year:04d}-{month_index + 1:02d}"


def _bounded_rating(value: float) -> float:
    return min(5.0, max(1.0, value))


def write_forecast_artifacts(result: dict[str, Any], output_dir: str | Path) -> None:
    """Write branch forecast/risk results as JSON."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "branch_forecasts.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
