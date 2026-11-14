"""Create a compact classification metrics table."""

from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

try:
    from mage_ai.data_preparation.decorators import test, transformer
except ModuleNotFoundError as error:
    if error.name != "mage_ai":
        raise

    def transformer(function):
        return function

    def test(function):
        return function


@transformer
def evaluate(df: pd.DataFrame, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """Return accuracy, macro precision, recall, and F1 for predictions."""
    y_true = df["target"]
    y_pred = df["predicted"]
    return pd.DataFrame(
        {
            "metric": ["accuracy", "precision", "recall", "f1_score"],
            "value": [
                round(accuracy_score(y_true, y_pred), 3),
                round(precision_score(y_true, y_pred, average="macro", zero_division=0), 3),
                round(recall_score(y_true, y_pred, average="macro", zero_division=0), 3),
                round(f1_score(y_true, y_pred, average="macro", zero_division=0), 3),
            ],
        }
    )


@test
def test_output(output: pd.DataFrame, *args) -> None:
    assert output["metric"].tolist() == ["accuracy", "precision", "recall", "f1_score"]
    assert output["value"].between(0, 1).all()
