import argparse
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model

from .data_utils import apply_zscore, invert_zscore, load_metadata


def recursive_forecast_with_loaded_model(model, metadata: dict, recent_values: np.ndarray, horizon_hours: int) -> np.ndarray:
    lookback = int(metadata["lookback_hours"])
    mean = float(metadata["mean"])
    std = float(metadata["std"])

    if recent_values.shape[0] < lookback:
        raise ValueError(f"Need at least {lookback} recent values, got {recent_values.shape[0]}")

    seq = apply_zscore(recent_values[-lookback:].astype(np.float32), mean, std).reshape(1, lookback, 1)

    preds_norm = []
    for _ in range(horizon_hours):
        next_norm = float(model.predict(seq, verbose=0)[0][0])
        preds_norm.append(next_norm)
        seq = np.append(seq[:, 1:, :], [[[next_norm]]], axis=1)

    return invert_zscore(np.array(preds_norm, dtype=np.float32), mean, std)


def recursive_forecast(model_path: str, metadata_path: str, recent_values: np.ndarray, horizon_hours: int) -> np.ndarray:
    metadata = load_metadata(Path(metadata_path))
    model = load_model(model_path, compile=False)
    return recursive_forecast_with_loaded_model(model, metadata, recent_values, horizon_hours)


def main():
    parser = argparse.ArgumentParser(description="Recursive multi-step sea level forecast.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--recent", required=True, help="Comma-separated recent values")
    parser.add_argument("--horizon", type=int, default=6)
    args = parser.parse_args()

    recent = np.array([float(v) for v in args.recent.split(",")], dtype=np.float32)
    preds = recursive_forecast(args.model, args.metadata, recent, args.horizon)
    print(preds.tolist())


if __name__ == "__main__":
    main()
