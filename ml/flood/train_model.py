import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
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
    """Find the first CSV file inside the dataset folder."""

    if not os.path.exists(DATASET_FOLDER):
        raise FileNotFoundError(
            "Dataset folder does not exist."
        )

    csv_files = [
        file for file in os.listdir(DATASET_FOLDER)
        if file.lower().endswith(".csv")
    ]

    if not csv_files:
        raise FileNotFoundError(
            "No CSV dataset found inside ml/flood/dataset/"
        )

    return os.path.join(DATASET_FOLDER, csv_files[0])


def clean_column_names(data):
    """Make column names easier to work with."""

    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return data


def find_target_column(data):
    """
    Try to identify the flood target column.
    """

    possible_targets = [
        "flood",
        "flood_risk",
        "flood_occurrence",
        "is_flood",
        "target",
        "label"
    ]

    for column in possible_targets:

        if column in data.columns:
            return column

    raise ValueError(
        "Could not find the flood target column. "
        "Please check the dataset column names."
    )


def prepare_data(data, target_column):

    # Remove completely empty columns
    data = data.dropna(axis=1, how="all")

    # Remove rows without target values
    data = data.dropna(subset=[target_column])

    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Convert categorical columns into numerical values
    X = pd.get_dummies(X, drop_first=True)

    # Convert all remaining values to numeric where possible
    X = X.apply(pd.to_numeric, errors="coerce")

    # Replace missing feature values with median
    X = X.fillna(X.median(numeric_only=True))

    # Remove columns that are still completely empty
    X = X.dropna(axis=1, how="all")

    return X, y


def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

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

    return accuracy, precision, recall, f1


def main():

    print("\nAASRA Flood Risk Model Training")
    print("--------------------------------")

    dataset_path = find_dataset()

    print(f"Dataset found: {dataset_path}")

    data = pd.read_csv(dataset_path)

    print(f"Dataset shape: {data.shape}")

    data = clean_column_names(data)

    print("\nDataset columns:")
    print(list(data.columns))

    target_column = find_target_column(data)

    print(f"\nTarget column: {target_column}")

    X, y = prepare_data(data, target_column)

    print(f"\nFeatures used: {list(X.columns)}")
    print(f"Number of features: {X.shape[1]}")

    # Check whether classification is possible
    if y.nunique() < 2:
        raise ValueError(
            "The target column must contain at least two classes."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    models = {

        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000
                )
            )
        ]),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        )
    }

    results = {}

    print("\nTraining models...")

    for name, model in models.items():

        print(f"\nTraining: {name}")

        model.fit(X_train, y_train)

        accuracy, precision, recall, f1 = evaluate_model(
            model,
            X_test,
            y_test
        )

        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")

    # Select the model with the highest F1 score
    best_name = max(
        results,
        key=lambda name: results[name]["f1"]
    )

    best_model = results[best_name]["model"]

    print("\n--------------------------------")
    print(f"Best model: {best_name}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            best_model.predict(X_test),
            zero_division=0
        )
    )

    model_path = os.path.join(
        MODEL_FOLDER,
        "flood_model.joblib"
    )

    model_data = {
        "model": best_model,
        "features": list(X.columns),
        "target": target_column,
        "model_name": best_name
    }

    joblib.dump(
        model_data,
        model_path
    )

    print("--------------------------------")
    print(f"Model saved to: {model_path}")
    print("Training completed successfully.")


if __name__ == "__main__":
    main()
