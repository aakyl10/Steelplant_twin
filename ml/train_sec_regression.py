"""Proof-of-concept SEC regression pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from simulator.generator import EXPECTED_ROW_COUNT, generate_telemetry

matplotlib.use("Agg")

from matplotlib import pyplot as plt  # noqa: E402

TARGET_COLUMN = "SEC"
METADATA_COLUMNS = ["timestamp"]
FEATURE_COLUMNS = [
    "ambient_temperature",
    "compressed_air_demand",
    "pressure_setpoint",
    "compressor_1_state",
    "compressor_2_state",
    "compressor_2_load_level",
    "active_compressors_count",
    "total_airflow",
    "pressure_deviation",
]
ML_DATASET_COLUMNS = METADATA_COLUMNS + FEATURE_COLUMNS + [TARGET_COLUMN]
FORBIDDEN_FEATURES = {
    "total_power_consumption",
    "energy_consumption",
    "SEC",
    "timestamp",
}

DATASET_PATH = Path("data/processed/ml_dataset.csv")
ML_OUTPUT_DIR = Path("docs/ml")
DATA_CONTRACT_PATH = Path("docs/02_data_contract.md")
METRICS_PATH = ML_OUTPUT_DIR / "metrics.csv"
PREDICTIONS_PATH = ML_OUTPUT_DIR / "predictions.csv"
ACTUAL_VS_PREDICTED_PATH = ML_OUTPUT_DIR / "actual_vs_predicted_sec.png"
FEATURE_IMPORTANCE_PATH = ML_OUTPUT_DIR / "feature_importance.png"


def load_contract_fields(path: Path = DATA_CONTRACT_PATH) -> list[str]:
    """Read telemetry field names from the data contract table."""
    fields = []
    in_fields_table = False

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Field | JSON/Python type |"):
            in_fields_table = True
            continue
        if not in_fields_table:
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("|"):
            break

        field = line.split("|")[1].strip()
        if field:
            fields.append(field)

    if not fields:
        raise ValueError("no telemetry fields found in docs/02_data_contract.md")

    return fields


def validate_columns_against_contract() -> None:
    """Ensure ML columns use exact field names from the data contract."""
    contract_fields = set(load_contract_fields())
    required_columns = set(ML_DATASET_COLUMNS)
    missing_from_contract = sorted(required_columns - contract_fields)
    if missing_from_contract:
        raise ValueError(f"ML columns not found in data contract: {missing_from_contract}")


def build_ml_dataset() -> pd.DataFrame:
    """Generate the telemetry dataset and select ML columns."""
    validate_columns_against_contract()
    telemetry = pd.DataFrame(generate_telemetry())
    dataset = telemetry.loc[:, ML_DATASET_COLUMNS].copy()
    validate_ml_dataset(dataset)
    return dataset


def validate_ml_dataset(dataset: pd.DataFrame) -> None:
    """Validate row count, feature safety, and compressor-state consistency."""
    missing_columns = [column for column in ML_DATASET_COLUMNS if column not in dataset]
    if missing_columns:
        raise ValueError(f"missing ML dataset columns: {missing_columns}")

    if len(dataset) != EXPECTED_ROW_COUNT:
        raise ValueError(f"expected {EXPECTED_ROW_COUNT} rows, got {len(dataset)}")

    if dataset[ML_DATASET_COLUMNS].isna().any().any():
        raise ValueError("ML dataset contains missing values")

    forbidden_used = sorted(FORBIDDEN_FEATURES.intersection(FEATURE_COLUMNS))
    if forbidden_used:
        raise ValueError(f"forbidden features selected: {forbidden_used}")

    if dataset["timestamp"].duplicated().any():
        raise ValueError("timestamps must be unique")

    expected_active = dataset["compressor_1_state"] + dataset["compressor_2_state"]
    if not (dataset["active_compressors_count"] == expected_active).all():
        raise ValueError("active_compressors_count does not match compressor states")

    inactive_load = dataset.loc[
        dataset["compressor_2_state"] == 0,
        "compressor_2_load_level",
    ]
    if not (inactive_load == 0).all():
        raise ValueError("compressor_2_load_level must be 0 when compressor 2 is off")

    active_load = dataset.loc[
        dataset["compressor_2_state"] == 1,
        "compressor_2_load_level",
    ]
    if not active_load.between(40, 100).all():
        raise ValueError("compressor_2_load_level must be 40-100 when active")

    if not (dataset[TARGET_COLUMN] > 0).all():
        raise ValueError("SEC must be positive")


def chronological_split(
    dataset: pd.DataFrame,
    train_fraction: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split first 80% as train and last 20% as test."""
    split_index = int(len(dataset) * train_fraction)
    train = dataset.iloc[:split_index]
    test = dataset.iloc[split_index:]
    return (
        train[FEATURE_COLUMNS],
        test[FEATURE_COLUMNS],
        train[TARGET_COLUMN],
        test[TARGET_COLUMN],
    )


def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    """Calculate regression metrics."""
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": r2_score(y_true, y_pred),
    }


def train_models(
    x_train: pd.DataFrame,
    y_train: pd.Series,
) -> dict[str, LinearRegression | RandomForestRegressor]:
    """Train baseline and main regression models."""
    models: dict[str, LinearRegression | RandomForestRegressor] = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            random_state=42,
        ),
    }

    for model in models.values():
        model.fit(x_train, y_train)

    return models


def save_actual_vs_predicted_plot(predictions: pd.DataFrame) -> None:
    """Save actual vs predicted SEC plot for both models."""
    plt.figure(figsize=(10, 5))
    plt.plot(
        predictions["timestamp"],
        predictions["actual_SEC"],
        label="Actual SEC",
        linewidth=2,
    )
    plt.plot(
        predictions["timestamp"],
        predictions["linear_regression_predicted_SEC"],
        label="Linear Regression",
        alpha=0.8,
    )
    plt.plot(
        predictions["timestamp"],
        predictions["random_forest_predicted_SEC"],
        label="Random Forest",
        alpha=0.8,
    )
    step = max(len(predictions) // 6, 1)
    plt.xticks(predictions["timestamp"].iloc[::step], rotation=30, ha="right")
    plt.ylabel("SEC")
    plt.title("Actual vs Predicted SEC")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ACTUAL_VS_PREDICTED_PATH, dpi=150)
    plt.close()


def save_feature_importance_plot(model: RandomForestRegressor) -> None:
    """Save Random Forest feature importance plot."""
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
    importances = importances.sort_values()

    plt.figure(figsize=(8, 5))
    importances.plot(kind="barh")
    plt.xlabel("Importance")
    plt.title("Random Forest Feature Importance")
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=150)
    plt.close()


def run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run dataset export, model training, evaluation, and artifact saving."""
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = build_ml_dataset()
    dataset.to_csv(DATASET_PATH, index=False)

    x_train, x_test, y_train, y_test = chronological_split(dataset)
    models = train_models(x_train, y_train)

    linear_predictions = models["Linear Regression"].predict(x_test)
    forest_predictions = models["Random Forest"].predict(x_test)

    metrics = pd.DataFrame(
        [
            {
                "model": "Linear Regression",
                **calculate_metrics(y_test, linear_predictions),
            },
            {
                "model": "Random Forest",
                **calculate_metrics(y_test, forest_predictions),
            },
        ]
    )
    metrics.to_csv(METRICS_PATH, index=False)

    predictions = pd.DataFrame(
        {
            "timestamp": dataset.iloc[len(x_train) :]["timestamp"].to_numpy(),
            "actual_SEC": y_test.to_numpy(),
            "linear_regression_predicted_SEC": linear_predictions,
            "random_forest_predicted_SEC": forest_predictions,
        }
    )
    predictions.to_csv(PREDICTIONS_PATH, index=False)

    save_actual_vs_predicted_plot(predictions)
    save_feature_importance_plot(models["Random Forest"])

    return metrics, predictions


def main() -> None:
    """Run the SEC regression pipeline from the command line."""
    metrics, _predictions = run_pipeline()
    print("Saved ML dataset and model outputs.")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
