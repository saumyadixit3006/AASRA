import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


def load_model(disaster: str):
    """
    Load a trained AASRA ML model.
    """

    model_paths = {
        "flood": os.path.join(
            BASE_DIR,
            "ml",
            "flood",
            "model",
            "flood_model.joblib"
        ),

        "cyclone": os.path.join(
            BASE_DIR,
            "ml",
            "cyclone",
            "model",
            "cyclone_model.joblib"
        ),

        "earthquake": os.path.join(
            BASE_DIR,
            "ml",
            "earthquake",
            "model",
            "earthquake_model.joblib"
        )
    }

    if disaster not in model_paths:
        raise ValueError(
            f"Unknown disaster type: {disaster}"
        )

    model_path = model_paths[disaster]

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"{disaster} model has not been trained yet."
        )

    return joblib.load(model_path)


def predict(
    disaster: str,
    input_data: dict
):
    """
    Run prediction using a trained AASRA model.
    """

    model_data = load_model(disaster)

    model = model_data["model"]
    features = model_data["features"]

    input_df = pd.DataFrame(
        [input_data]
    )

    input_df = pd.get_dummies(
        input_df,
        drop_first=True
    )

    input_df = input_df.reindex(
        columns=features,
        fill_value=0
    )

    prediction = model.predict(
        input_df
    )[0]

    confidence = None

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(
            input_df
        )

        confidence = float(
            probabilities.max()
        )

    return {
        "prediction": prediction,
        "confidence": confidence
    }
