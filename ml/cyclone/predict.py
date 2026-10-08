import os
import joblib
import pandas as pd


MODEL_PATH = "model/cyclone_model.joblib"


def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Cyclone model has not been trained yet."
        )

    return joblib.load(MODEL_PATH)


def predict_cyclone_risk(input_data: dict):

    model_data = load_model()

    model = model_data["model"]
    features = model_data["features"]

    input_df = pd.DataFrame([input_data])

    input_df = pd.get_dummies(
        input_df,
        drop_first=True
    )

    input_df = input_df.reindex(
        columns=features,
        fill_value=0
    )

    prediction = model.predict(input_df)[0]

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
