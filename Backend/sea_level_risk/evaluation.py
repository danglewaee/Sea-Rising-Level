import numpy as np


def _safe_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if y_true.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _safe_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if y_true.size == 0:
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)))


def evaluate_peak_metrics(y_true: np.ndarray, y_pred: np.ndarray, quantiles: tuple[float, ...] = (0.9, 0.95, 0.99)) -> dict:
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)

    result = {
        "overall_rmse": _safe_rmse(y_true, y_pred),
        "overall_mae": _safe_mae(y_true, y_pred),
    }

    for q in quantiles:
        threshold = float(np.quantile(y_true, q))
        mask = y_true >= threshold
        key = f"q{int(q * 100)}"
        result[f"{key}_threshold"] = threshold
        result[f"{key}_count"] = int(np.count_nonzero(mask))
        result[f"{key}_rmse"] = _safe_rmse(y_true[mask], y_pred[mask])
        result[f"{key}_mae"] = _safe_mae(y_true[mask], y_pred[mask])

    return result
