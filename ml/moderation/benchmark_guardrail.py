"""Official Held-out Test Split Benchmark for ModernBERT-TR Guardrail.

Evaluates the calibrated thresholds on the held-out TEST split of ytu-ce-cosmos/guardrail-tr.
Reports Sample Count, Precision, Recall, F1, Macro-F1, Weighted-F1, and per-category breakdown.
"""

import os
import json
import time
import urllib.request
import numpy as np
from typing import Dict, List, Any
import torch

from backend.app.moderation.base import HazardCategory
from backend.app.moderation.guardrail_classifier import ModernBERTGuardrailClassifier


def fetch_test_samples(max_samples: int = 1000) -> List[Dict[str, Any]]:
    """Fetch official held-out TEST split rows from HuggingFace Datasets Server."""
    print(f"[1] Fetching {max_samples} held-out TEST samples from ytu-ce-cosmos/guardrail-tr...")
    samples = []
    offset = 0
    limit = 100

    while len(samples) < max_samples:
        url = f"https://datasets-server.huggingface.co/rows?dataset=ytu-ce-cosmos/guardrail-tr&config=default&split=test&offset={offset}&limit={limit}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rows = data.get("rows", [])
                if not rows:
                    break
                for r in rows:
                    row_data = r.get("row", {})
                    samples.append(row_data)
                    if len(samples) >= max_samples:
                        break
                offset += len(rows)
        except Exception as e:
            print(f"  Warning during fetch at offset {offset}: {e}")
            break

    print(f"  Successfully fetched {len(samples)} TEST samples.")
    return samples


def run_test_benchmark(max_samples: int = 1000):
    samples = fetch_test_samples(max_samples=max_samples)
    if not samples:
        print("  Could not fetch TEST samples.")
        return None

    thresh_file = "backend/app/moderation/calibrated_thresholds.json"
    thresholds = {}
    if os.path.exists(thresh_file):
        with open(thresh_file, "r", encoding="utf-8") as f:
            cal_data = json.load(f)
            thresholds = cal_data.get("per_category_thresholds", {})
        print(f"[2] Loaded calibrated thresholds from '{thresh_file}'.")
    else:
        print("[2] Calibrated thresholds file not found, using default 0.50 thresholds.")

    classifier = ModernBERTGuardrailClassifier()
    texts = [s.get("prompt", s.get("text", "")) for s in samples]

    print(f"[3] Running inference on {len(texts)} TEST texts on {classifier.device}...")
    t_start = time.perf_counter()

    batch_size = 32
    all_scores = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        scores = classifier.batch_classify(batch_texts)
        all_scores.extend(scores)

    total_time_s = time.perf_counter() - t_start
    latency_per_sample_ms = (total_time_s / len(texts)) * 1000.0

    print(f"  Inference completed in {total_time_s:.2f}s ({latency_per_sample_ms:.2f} ms/sample).")

    # Evaluate metrics
    print("\n[4] Evaluating Metrics on Held-out TEST Split:")
    results_by_category: Dict[str, Any] = {}
    f1_list = []
    weights_list = []

    # 1. Evaluate overall unsafe
    y_true_unsafe = np.array([1 if s.get("safety") == 1 else 0 for s in samples])
    pred_unsafe = np.array([s.unsafe for s in all_scores])
    t_unsafe = thresholds.get("unsafe", 0.50)

    y_pred = (pred_unsafe >= t_unsafe).astype(int)
    tp = np.sum((y_true_unsafe == 1) & (y_pred == 1))
    fp = np.sum((y_true_unsafe == 0) & (y_pred == 1))
    fn = np.sum((y_true_unsafe == 1) & (y_pred == 0))

    p = float(tp / (tp + fp + 1e-12))
    r = float(tp / (tp + fn + 1e-12))
    unsafe_f1 = float(2 * p * r / (p + r + 1e-12))
    support = int(np.sum(y_true_unsafe))

    results_by_category["unsafe"] = {
        "threshold_used": t_unsafe,
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(unsafe_f1, 4),
        "support_positives": support,
        "support_negatives": int(np.sum(y_true_unsafe == 0)),
    }
    print(f"  {'unsafe':24s} | Threshold: {t_unsafe:.2f} | P: {p:.4f} | R: {r:.4f} | F1: {unsafe_f1:.4f} | Support: {support}")

    # 2. Evaluate each hazard category
    for cat in HazardCategory:
        if cat == HazardCategory.UNSAFE:
            continue
        cat_name = cat.value

        y_true = np.array([1 if cat_name in s.get("category", []) else 0 for s in samples])
        pred_probs = np.array([getattr(s, cat_name, 0.0) for s in all_scores])
        t = thresholds.get(cat_name, 0.50)

        y_pred = (pred_probs >= t).astype(int)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))

        p = float(tp / (tp + fp + 1e-12))
        r = float(tp / (tp + fn + 1e-12))
        f1 = float(2 * p * r / (p + r + 1e-12))

        support = int(np.sum(y_true))
        results_by_category[cat_name] = {
            "threshold_used": t,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "support_positives": support,
            "support_negatives": int(np.sum(y_true == 0)),
        }

        print(f"  {cat_name:24s} | Threshold: {t:.2f} | P: {p:.4f} | R: {r:.4f} | F1: {f1:.4f} | Support: {support}")

        if support > 0:
            f1_list.append(f1)
            weights_list.append(support)

    macro_f1 = float(np.mean(f1_list)) if f1_list else 0.0
    weighted_f1 = float(np.average(f1_list, weights=weights_list)) if weights_list and sum(weights_list) > 0 else 0.0

    print("\n-------------------------------------------------------------")
    print(f"  Overall Unsafe F1:   {unsafe_f1:.4f}")
    print(f"  Hazard Macro-F1:     {macro_f1:.4f}")
    print(f"  Hazard Weighted-F1:  {weighted_f1:.4f}")
    print("-------------------------------------------------------------")

    # Save benchmark results
    out_dir = "ml/evaluation/results"
    os.makedirs(out_dir, exist_ok=True)
    report = {
        "model_id": ModernBERTGuardrailClassifier.MODEL_ID,
        "dataset_name": "ytu-ce-cosmos/guardrail-tr",
        "dataset_split": "test",
        "evaluation_scope": "Sampled subset of 1,000 held-out TEST rows (from the ~405K total dataset)",
        "sample_count": len(samples),
        "device": str(classifier.device),
        "latency_per_sample_ms": round(latency_per_sample_ms, 2),
        "overall_unsafe_f1": round(unsafe_f1, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_category_metrics": results_by_category,
    }

    out_file = os.path.join(out_dir, "guardrail_test_evaluation.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Saved benchmark report to '{out_file}'.")
    return report


if __name__ == "__main__":
    run_test_benchmark()
