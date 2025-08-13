from fastapi import FastAPI
from pydantic import create_model
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient

MODEL_NAME = "bearing-failure-model"

# Load latest Production-tagged model
client = MlflowClient()
versions = client.search_model_versions(f"name='{MODEL_NAME}'")
prod_versions = [v for v in versions if v.tags.get("deployment_stage") == "production"]

if not prod_versions:
    raise RuntimeError("No production model found with tag 'deployment_stage=production'")

latest_prod_version = sorted(prod_versions, key=lambda v: int(v.version), reverse=True)[0].version
model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{latest_prod_version}")

# Get required features from model
input_features = list(model.feature_names_in_)
fields = {name: (float, ...) for name in input_features}
BearingFeatures = create_model("BearingFeatures", **fields)

app = FastAPI(title="Bearing Failure Prediction API")

@app.post("/predict")
def predict(input_data: BearingFeatures):
    data_df = pd.DataFrame([input_data.dict()])
    prediction = model.predict(data_df)[0]
    return {"prediction": int(prediction)}
