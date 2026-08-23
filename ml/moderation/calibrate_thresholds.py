"""Threshold calibration script for ModernBERT-TR Guardrail on guardrail-tr DEV split.

Fetches official validation (DEV) split samples from Hugging Face Datasets API.
Optimizes per-category decision thresholds on DEV to maximize F1, with safety margins
for severe categories (CSAE, SELF_HARM_SUICIDE).

CRITICAL SCIENTIFIC PRINCIPLE:
- The TEST split remains strictly held out and is NEVER accessed during calibration.
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


def fetch_dev_samples(max_samples: int = 1000) -> List[Dict[str, Any]]:
    """Fetch official validation (DEV) rows from HuggingFace Datasets Server."""
    print(f"[1] Fetching {max_samples} validation (DEV) samples from ytu-ce-cosmos/guardrail-tr...")
    samples = []
    offset = 0
    limit = 100

    while len(samples) < max_samples:
        url = f"https://datasets-server.huggingface.co/rows?dataset=ytu-ce-cosmos/guardrail-tr&config=default&split=validation&offset={offset}&limit={limit}"
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

    print(f"  Successfully fetched {len(samples)} DEV samples.")
    return samples


def calibrate_thresholds(max_samples: int = 1000):
    samples = fetch_dev_samples(max_samples=max_samples)
    if not samples:
        print("  Could not fetch DEV samples, using fallback calibrated defaults.")
        return

    classifier = ModernBERTGuardrailClassifier()
    texts = [s.get("prompt", s.get("text", "")) for s in samples]

    print(f"[2] Running inference on {len(texts)} DEV texts on {classifier.device}...")
    t_start = time.perf_counter()
    batch_size = 32
    all_scores = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        scores = classifier.batch_classify(batch_texts)
        all_scores.extend(scores)

    dur = time.perf_counter() - t_start
    print(f"  Inference finished in {dur:.2f}s ({(dur/len(texts))*1000:.1f} ms/text).")

    print("[3] Searching optimal F1 decision threshold per category on DEV split...")
    calibrated_thresholds: Dict[str, float] = {}
    dev_metrics_summary: Dict[str, Any] = {}

    threshold_candidates = np.arange(0.10, 0.90, 0.05)

    # 1. Unsafe binary threshold
    y_true_unsafe = np.array([1 if s.get("safety") == 1 else 0 for s in samples])
    pred_unsafe = np.array([s.unsafe for s in all_scores])

    best_unsafe_t = 0.50
    best_unsafe_f1 = -1.0
    best_unsafe_p, best_unsafe_r = 0.0, 0.0

    for t in threshold_candidates:
        y_pred = (pred_unsafe >= t).astype(int)
        tp = np.sum((y_true_unsafe == 1) & (y_pred == 1))
        fp = np.sum((y_true_unsafe == 0) & (y_pred == 1))
        fn = np.sum((y_true_unsafe == 1) & (y_pred == 0))

        p = tp / (tp + fp + 1e-12)
        r = tp / (tp + fn + 1e-12)
        f1 = 2 * p * r / (p + r + 1e-12)

        if f1 > best_unsafe_f1:
            best_unsafe_f1 = f1
            best_unsafe_t = round(float(t), 2)
            best_unsafe_p, best_unsafe_r = float(p), float(r)

    calibrated_thresholds["unsafe"] = best_unsafe_t
    dev_metrics_summary["unsafe"] = {
        "calibrated_threshold": best_unsafe_t,
        "dev_precision": round(best_unsafe_p, 4),
        "dev_recall": round(best_unsafe_r, 4),
        "dev_f1": round(best_unsafe_f1, 4),
        "support": int(np.sum(y_true_unsafe)),
    }
    print(f"  Category 'unsafe': Optimal Thresh = {best_unsafe_t:.2f} (F1: {best_unsafe_f1:.4f}, P: {best_unsafe_p:.4f}, R: {best_unsafe_r:.4f})")

    # 2. Per hazard category threshold
    for cat in HazardCategory:
        if cat == HazardCategory.UNSAFE:
            continue
        cat_name = cat.value

        y_true_cat = np.array([
            1 if cat_name in s.get("category", []) else 0 for s in samples
        ])
        pred_cat = np.array([getattr(s, cat_name, 0.0) for s in all_scores])
        support_pos = int(np.sum(y_true_cat))

        if support_pos == 0:
            calibrated_thresholds[cat_name] = 0.50
            continue

        best_t = 0.50
        best_metric = -1.0
        best_p, best_r = 0.0, 0.0

        for t in threshold_candidates:
            y_pred = (pred_cat >= t).astype(int)
            tp = np.sum((y_true_cat == 1) & (y_pred == 1))
            fp = np.sum((y_true_cat == 0) & (y_pred == 1))
            fn = np.sum((y_true_cat == 1) & (y_pred == 0))

            p = tp / (tp + fp + 1e-12)
            r = tp / (tp + fn + 1e-12)
            f1 = 2 * p * r / (p + r + 1e-12)

            if cat in [HazardCategory.CSAE, HazardCategory.SELF_HARM_SUICIDE]:
                metric = f1 + (0.3 * r)
            else:
                metric = f1

            if metric > best_metric:
                best_metric = metric
                best_t = round(float(t), 2)
                best_p, best_r = float(p), float(r)

        cat_f1 = 2 * best_p * best_r / (best_p + best_r + 1e-12)
        calibrated_thresholds[cat_name] = best_t
        dev_metrics_summary[cat_name] = {
            "calibrated_threshold": best_t,
            "dev_precision": round(best_p, 4),
            "dev_recall": round(best_r, 4),
            "dev_f1": round(cat_f1, 4),
            "support": support_pos,
        }
        print(f"  Category '{cat_name:24s}': Optimal Thresh = {best_t:.2f} (F1: {cat_f1:.4f}, P: {best_p:.4f}, R: {best_r:.4f}, Supp: {support_pos})")

    out_file = "backend/app/moderation/calibrated_thresholds.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    payload = {
        "dataset": "ytu-ce-cosmos/guardrail-tr",
        "split_used": "validation (DEV)",
        "objective": "Max F1 on DEV with severe harm safety margin",
        "sample_count": len(samples),
        "per_category_thresholds": calibrated_thresholds,
        "dev_metrics": dev_metrics_summary,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n[4] Saved calibrated thresholds to '{out_file}'.")


if __name__ == "__main__":
    calibrate_thresholds()
