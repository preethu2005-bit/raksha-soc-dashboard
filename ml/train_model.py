from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report


# Locate project files
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "ml" / "training_data.csv"
MODEL_PATH = PROJECT_DIR / "backend" / "model.joblib"


def main():
    # Check that the dataset exists
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_PATH}"
        )

    # Load the dataset
    data = pd.read_csv(DATA_PATH)

    required_columns = {"raw_log", "label"}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            "CSV must contain raw_log and label columns"
        )

    # Clean the dataset
    data = data.dropna(subset=["raw_log", "label"])

    data["raw_log"] = data["raw_log"].astype(str).str.strip()
    data["label"] = data["label"].astype(str).str.strip()

    data = data[
        (data["raw_log"] != "") &
        (data["label"] != "")
    ]

    # Validate labels
    valid_labels = {"Benign", "Suspicious", "Malicious"}

    if not set(data["label"]).issubset(valid_labels):
        raise ValueError(
            "Labels must be Benign, Suspicious, or Malicious"
        )

    if data["label"].nunique() < 3:
        raise ValueError(
            "Training data must contain all three classes"
        )

    # Check dataset size and class distribution
    class_counts = data["label"].value_counts()

    if len(data) < 15:
        raise ValueError(
            "Please provide at least 15 labeled examples "
            "for a train/test split"
        )

    if class_counts.min() < 2:
        raise ValueError(
            "Each class needs at least 2 examples "
            "for a train/test split"
        )

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data["raw_log"],
        data["label"],
        test_size=0.2,
        random_state=42,
        stratify=data["label"]
    )

    # Create the TF-IDF + Logistic Regression pipeline
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

    # Train using only the training data
    model.fit(X_train, y_train)

    # Evaluate on held-out test data
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    f1_macro = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    f1_weighted = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    # Display evaluation metrics
    print("\n===== MODEL EVALUATION =====")
    print(f"Dataset examples: {len(data)}")
    print(f"Training examples: {len(X_train)}")
    print(f"Testing examples: {len(X_test)}")
    print(f"Classes: {sorted(data['label'].unique())}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy:.1%})")
    print(f"Macro F1-score: {f1_macro:.4f}")
    print(f"Weighted F1-score: {f1_weighted:.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=sorted(valid_labels),
            zero_division=0
        )
    )

    # Retrain the final model using all labeled data
    # after evaluating performance on the held-out test set.
    final_model = Pipeline([
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

    final_model.fit(data["raw_log"], data["label"])

    # Save the final model for the Flask backend
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)

    print("\nModel training completed successfully!")
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
