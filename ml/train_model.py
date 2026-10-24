
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Locate project files
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "ml" / "training_data.csv"
MODEL_PATH = PROJECT_DIR / "backend" / "model.joblib"


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = {"raw_log", "label"}
    if not required_columns.issubset(data.columns):
        raise ValueError(
            "CSV must contain raw_log and label columns"
        )

    data = data.dropna(subset=["raw_log", "label"])
    data["raw_log"] = data["raw_log"].astype(str).str.strip()
    data["label"] = data["label"].astype(str).str.strip()
    data = data[
        (data["raw_log"] != "") & (data["label"] != "")
    ]

    valid_labels = {"Benign", "Suspicious", "Malicious"}
    if not set(data["label"]).issubset(valid_labels):
        raise ValueError(
            "Labels must be Benign, Suspicious, or Malicious"
        )

    if data["label"].nunique() < 3:
        raise ValueError(
            "Training data must contain all three classes"
        )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    model.fit(data["raw_log"], data["label"])

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model training completed successfully!")
    print(f"Training examples: {len(data)}")
    print(f"Classes: {sorted(data['label'].unique())}")
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
