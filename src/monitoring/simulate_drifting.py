import os
import pandas as pd
import numpy as np
from pathlib import Path

# === CONFIGURATION ===
RAW_ROOT = Path("data/raw/Nasa-Bearing")
DRIFTED_ROOT = Path("data/drifted")
TEST_SETS = ["1st_test"]
FILES_TO_DRIFT = 10  # Number of files per test set for PoC
DRIFT_TYPE = "mean_shift"  # Options: "mean_shift", "gaussian_noise", "feature_dropout"

# === DRIFT PARAMETERS ===
MEAN_SHIFT = 10.0
NOISE_STD = 5.0
DROPOUT_RATE = 0.5

# === DRIFT METHODS ===
def apply_mean_shift(df, shift=MEAN_SHIFT):
    return df + shift

def apply_gaussian_noise(df, std=NOISE_STD):
    noise = np.random.normal(0, std, df.shape)
    return df + noise

def apply_feature_dropout(df, rate=DROPOUT_RATE):
    mask = np.random.rand(*df.shape) > rate
    return df.where(mask, np.nan).fillna(0)

DRIFT_FUNCTIONS = {
    "mean_shift": apply_mean_shift,
    "gaussian_noise": apply_gaussian_noise,
    "feature_dropout": apply_feature_dropout,
}

# === MAIN DRIFTING LOGIC ===
def generate_drifted_poc():
    drift_fn = DRIFT_FUNCTIONS[DRIFT_TYPE]

    for test_set in TEST_SETS:
        input_dir = RAW_ROOT / test_set / test_set
        output_dir = DRIFTED_ROOT / test_set
        output_dir.mkdir(parents=True, exist_ok=True)

        all_files = sorted(f for f in input_dir.iterdir() if f.is_file())
        files = all_files[:FILES_TO_DRIFT]

        print(f"[i] Drifting {len(files)} files from {input_dir} -> {output_dir}")

        for file_path in files:
            df = pd.read_csv(file_path, sep=r"\s+", header=None)
            df_drifted = drift_fn(df)
            output_path = output_dir / file_path.name
            df_drifted.to_csv(output_path, sep="\t", index=False, header=False, float_format="%.6f")

        print(f"[✓] Done: {len(files)} files drifted to {output_dir}")

if __name__ == "__main__":
    generate_drifted_poc()
