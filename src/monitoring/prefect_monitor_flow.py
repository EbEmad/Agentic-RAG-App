# src/monitoring/prefect_monitor_flow.py
import sys, os
from io import StringIO
import boto3
import pandas as pd
from prefect import flow, task

# Ensure both original source path and the temp deployment path are covered
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from monitoring.drift_check import run_drift
from monitoring.alert import send_teams_alert
from monitoring.workflow_trigger import trigger_retrain

# --- Configuration ---
BUCKET_NAME = "mlops-project-artifacts-noura"
REFERENCE_PREFIX = "dataset/raw/Nasa-Bearing/1st_test/1st_test/"
CURRENT_PREFIX = "dataset/drifted/1st_test/"
MAX_FILES = 10

def read_s3_file(s3_client, bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(StringIO(response["Body"].read().decode()), sep="\t", header=None)
    except Exception as e:
        print(f"[ERROR] Failed to read S3 file: {key} — {e}")
        return None  # Let the loader skip this file

def load_data_from_s3(limit=MAX_FILES):
    s3 = boto3.client("s3")

    # List files from S3
    ref_objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=REFERENCE_PREFIX).get("Contents", [])
    cur_objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=CURRENT_PREFIX).get("Contents", [])

    # Filter only .txt files
    ref_keys = [obj["Key"] for obj in ref_objects][:limit]
    cur_keys = [obj["Key"] for obj in cur_objects]

    print(f"[DEBUG] Found {len(ref_keys)} reference files and {len(cur_keys)} current files.")

    # Load reference data
    ref_dfs = []
    for key in ref_keys:
        df = read_s3_file(s3, BUCKET_NAME, key)
        if df is not None:
            print(f"[DEBUG] Loaded reference file {key} with shape {df.shape}")
            ref_dfs.append(df)

    if not ref_dfs:
        raise ValueError(f"No reference data found or loaded from S3 at {REFERENCE_PREFIX}")

    reference = pd.concat(ref_dfs, ignore_index=True)

    # Load current data
    cur_dfs = []
    for key in cur_keys:
        df = read_s3_file(s3, BUCKET_NAME, key)
        if df is not None:
            print(f"[DEBUG] Loaded current file {key} with shape {df.shape}")
            cur_dfs.append(df)

    if not cur_dfs:
        raise ValueError(f"No current data found or loaded from S3 at {CURRENT_PREFIX}")

    current = pd.concat(cur_dfs, ignore_index=True)

    # Assign sensor column names
    reference.columns = current.columns = [f"sensor_{i+1}" for i in range(reference.shape[1])]

    return reference, current


@task
def check_drift(reference, current):
    drift_score, drift_detected, _ = run_drift(reference, current)
    return drift_score, drift_detected


@flow
def monitor_pipeline():
    reference, current = load_data_from_s3()
    drift_score, drift_detected = check_drift(reference, current)

    if drift_detected or drift_score > 0.1:
        print("⚠️ Drift detected.")
        send_teams_alert("⚠️ Drift detected! Retraining pipeline started for bearing failure prediction.")
        trigger_retrain()
    else:
        print("✅ No significant drift detected.")


if __name__ == "__main__":
    monitor_pipeline()
