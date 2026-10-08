import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


DATASET_FOLDER = "dataset"
MODEL_FOLDER = "model"

os.makedirs(MODEL_FOLDER, exist_ok=True)


def find_dataset():

    if not os.path.exists(DATASET_FOLDER):
        raise FileNotFoundError(
            "Create the dataset folder inside ml/earthquake/"
        )

    files = [
        file for file in os.listdir(DATASET_FOLDER)
        if file.lower().endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError(
            "No CSV dataset found inside ml/earthquake/dataset/"
        )

    return os.path.join(DATASET_FOLDER, files[0])


def main():

    print("\nAASRA Earthquake Risk Model")
    print("---------------------------")

    dataset_path = find_dataset()

    data = pd.read_csv(dataset_path)

    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    print("Dataset shape:", data.shape)
    print("Columns:", list(data.columns))

    possible_targets = [
        "risk",
        "risk_level",
        "earthquake_risk",
        "severity",
        "target",
        "label"
    ]

    target = None

    for column in possible_targets:

        if column in data.columns:
            target = column
            break

    if target is None:
        raise ValueError(
            "Could not identify the earthquake target column."
        )

    data = data.dropna(subset=[target])

    X = data.drop(columns=[target])
    y = data[target]

    X = pd.get_dummies(
        X,
        drop_first=True
    )

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.fillna(
        X.median(numeric_only=True)
    )

    if y.nunique() < 2:
        raise ValueError(
            "Earthquake target must contain at least two classes."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    print("\nTraining model...")

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("\nModel Performance")
    print("-----------------")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    model_data = {
        "model": model,
        "features": list(X.columns),
        "target": target
    }

    model_path = os.path.join(
        MODEL_FOLDER,
        "earthquake_model.joblib"
    )

    joblib.dump(
        model_data,
        model_path
    )

    print(
        "\nModel saved:",
        model_path
    )


if __name__ == "__main__":
    main()
