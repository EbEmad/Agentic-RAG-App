# src/monitoring/workflow_trigger.py
#import subprocess
from prefect.deployments import run_deployment

def trigger_retrain():
    # Run the existing deployment pipeline (acts as retrain)
    run_deployment("Bearing Failure Prediction Pipeline/deployment-pipeline")
    print("Deployment pipeline triggered due to drift.")

def switch_model():
    # Optional: use MLflow to switch model version
    pass
