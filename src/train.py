import os
import boto3
import pandas as pd
import mlflow
import mlflow.sklearn
from io import BytesIO, StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Configuration
S3_BUCKET = "mlops-project-artifacts-noura"
FEATURES_KEY = "dataset/processed/features.csv"
#MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri("http://3.215.80.166:5050")
MLFLOW_EXPERIMENT = "bearing_failure_prediction"
MODEL_NAME = "bearing-failure-model"

# Initialize S3 and MLflow
s3 = boto3.client("s3")
#mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT)
client = mlflow.tracking.MlflowClient()


def load_data_from_s3(bucket: str, key: str):
    """
    Download features.csv from S3 into a pandas DataFrame.
    """
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(BytesIO(obj["Body"].read()))
    # Split into X, y
    X = df.drop(columns=["filename", "source", "label"], errors='ignore')
    y = df["label"]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_and_log_model(X_train, X_test, y_train, y_test, max_depth: int):
    """
    Train RandomForestClassifier, log parameters, metrics, and model artifact to MLflow.
    """
    with mlflow.start_run() as run:
        clf = RandomForestClassifier(n_estimators=100, max_depth=max_depth, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        # Log to MLflow
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(clf, artifact_path="model", registered_model_name=MODEL_NAME)

        print(f"Trained depth={max_depth}, accuracy={acc:.4f} (run_id={run.info.run_id})")
        return run.info.run_id, acc


def promote_if_best(best_run_id: str, best_acc: float):
    """
    Compare best model accuracy with current production stage, and promote if improved.
    """
    # Attempt to get existing production model
    try:
        prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        if prod_versions:
            prod_run_id = prod_versions[0].run_id
            prod_acc = float(client.get_run(prod_run_id).data.metrics.get("accuracy", 0))
            print(f"Current Production accuracy: {prod_acc:.4f} (run {prod_run_id})")
        else:
            prod_acc = 0
            print("No model in Production stage yet.")
    except Exception as e:
        prod_acc = 0
        print(f"Could not fetch Production model info: {e}")

    if best_acc > prod_acc:
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=client.get_latest_versions(MODEL_NAME, stages=["None"])[-1].version,
            stage="Production",
            archive_existing_versions=True
        )
        print(f"Promoted run {best_run_id} to Production stage.")
    else:
        print("Best model did not improve, no promotion performed.")


def train_model_main():
    X_train, X_test, y_train, y_test = load_data_from_s3(S3_BUCKET, FEATURES_KEY)
    best_acc = 0.0
    best_run_id = None

    for depth in [5, 10, 15]:
        run_id, acc = train_and_log_model(X_train, X_test, y_train, y_test, depth)
        if acc > best_acc:
            best_acc = acc
            best_run_id = run_id

    print(f"Best run: {best_run_id} with accuracy {best_acc:.4f}")
    promote_if_best(best_run_id, best_acc)


if __name__ == "__main__":
    train_model_main()
