import os
import boto3
import pandas as pd
import numpy as np
from io import BytesIO, StringIO

# Configuration
S3_BUCKET = "mlops-project-artifacts-noura"
S3_PREFIX = "dataset/raw/Nasa-Bearing"
TEST_SETS = ["1st_test", "2nd_test", "3rd_test"]
S3_OUTPUT_PATH = "dataset/processed/features.csv"

# Initialize S3 client
s3 = boto3.client('s3')

def read_s3_file(bucket: str, key: str) -> pd.DataFrame:
    """
    Download a text file from S3 and load it into a pandas DataFrame.
    Assumes whitespace-separated values with no header.
    """
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(
        BytesIO(obj['Body'].read()),
        sep=r"\s+",
        header=None
    )

def extract_features_from_df(df: pd.DataFrame) -> dict:
    """
    Given a DataFrame of signal data (columns as separate signals),
    compute statistical features for each column.
    Returns a dict of feature name → value.
    """
    features = {}
    for col in df.columns:
        signal = df[col]
        features[f"mean_{col}"] = signal.mean()
        features[f"rms_{col}"] = np.sqrt(np.mean(signal**2))
        features[f"std_{col}"] = signal.std()
        features[f"kurtosis_{col}"] = signal.kurtosis()
        features[f"skew_{col}"] = signal.skew()
        features[f"peak_{col}"] = signal.max()
    return features


def extract_features_main():
    feature_rows = []

    for test_set in TEST_SETS:
        prefix = f"{S3_PREFIX}/{test_set}/{test_set}/"
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

        for page in page_iterator:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith('/'):
                    continue
                try:
                    df = read_s3_file(S3_BUCKET, key)
                    features = extract_features_from_df(df)
                    features['filename'] = os.path.basename(key)
                    features['source'] = test_set
                    feature_rows.append(features)
                except Exception as e:
                    print(f"Skipped file {key} due to error: {e}")

    # Build DataFrame
    features_df = pd.DataFrame(feature_rows)

    # Label last 10% of files in each set as failure
    features_df['label'] = 0
    for test_set in TEST_SETS:
        idx = features_df[features_df['source'] == test_set].index.tolist()
        cutoff = int(len(idx) * 0.9)
        for i in idx[cutoff:]:
            features_df.at[i, 'label'] = 1

    # Write features to S3
    csv_buffer = StringIO()
    features_df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=S3_BUCKET, Key=S3_OUTPUT_PATH, Body=csv_buffer.getvalue())
    print(f"Saved features for {len(features_df)} files to s3://{S3_BUCKET}/{S3_OUTPUT_PATH}")


if __name__ == '__main__':
    extract_features_main()
