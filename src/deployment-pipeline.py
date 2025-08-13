# src/pipeline.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root

from prefect import flow, task
from src.extract_features import extract_features_main
from datetime import timedelta
from src.train import train_model_main
@task(
    persist_result=True,  # Cache results so we don’t recompute on reruns
    cache_expiration=timedelta(days=1),  # Cache valid for 1 day
    retries=0  # No automatic retries; you can restart failed tasks via UI
)
def extract_features():
    extract_features_main()

@task
def train_model():
    train_model_main()  # Your existing function

@flow(name="Bearing Failure Prediction Pipeline")
def full_pipeline(start_step: str = "extract"):
    # print("Starting Feature Extraction...")
    # extract_features()
    # print("Feature Extraction Done!")

    # print("Starting Model Training...")
    # train_model()
    # print("Model Training Done!")
    
    if start_step == "extract":
        features = extract_features()
        train_model()
    elif start_step == "train":
        train_model()
    else:
        raise ValueError(f"Invalid start_step: {start_step}. Use 'extract' or 'train'.")

if __name__ == "__main__":
    full_pipeline()
