import pandas as pd
import pytest

from ml.train_sec_regression import (
    FEATURE_COLUMNS,
    FORBIDDEN_FEATURES,
    TARGET_COLUMN,
    build_ml_dataset,
    chronological_split,
    load_contract_fields,
    validate_ml_dataset,
)
from simulator.generator import EXPECTED_ROW_COUNT


def test_feature_columns_do_not_include_forbidden_features():
    assert TARGET_COLUMN not in FEATURE_COLUMNS
    assert not FORBIDDEN_FEATURES.intersection(FEATURE_COLUMNS)


def test_ml_columns_match_data_contract():
    contract_fields = set(load_contract_fields())

    assert TARGET_COLUMN in contract_fields
    for column in FEATURE_COLUMNS:
        assert column in contract_fields


def test_build_ml_dataset_has_expected_shape_and_columns():
    dataset = build_ml_dataset()

    assert len(dataset) == EXPECTED_ROW_COUNT
    assert "timestamp" in dataset.columns
    assert TARGET_COLUMN in dataset.columns
    for column in FEATURE_COLUMNS:
        assert column in dataset.columns


def test_chronological_split_uses_first_80_percent_for_training():
    dataset = build_ml_dataset()
    x_train, x_test, y_train, y_test = chronological_split(dataset)

    assert len(x_train) == int(EXPECTED_ROW_COUNT * 0.8)
    assert len(x_test) == EXPECTED_ROW_COUNT - len(x_train)
    assert y_train.index.max() < y_test.index.min()


def test_validation_rejects_missing_values():
    dataset = build_ml_dataset()
    dataset.loc[0, "ambient_temperature"] = pd.NA

    with pytest.raises(ValueError, match="missing values"):
        validate_ml_dataset(dataset)


def test_validation_rejects_contradictory_compressor_2_load():
    dataset = build_ml_dataset()
    inactive_index = dataset.index[dataset["compressor_2_state"] == 0][0]
    dataset.loc[inactive_index, "compressor_2_load_level"] = 50.0

    with pytest.raises(ValueError, match="compressor_2_load_level"):
        validate_ml_dataset(dataset)
