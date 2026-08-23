"""Generate report-ready figures, tables, data exports, and diagrams for TEKNOFEST Report."""

import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configure high-quality styling for publication
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#334155"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#E2E8F0"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["grid.alpha"] = 0.7

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "docs", "report_assets")
DATA_DIR = os.path.join(ASSETS_DIR, "data")
CHARTS_DIR = os.path.join(ASSETS_DIR, "charts")
DIAGRAMS_DIR = os.path.join(ASSETS_DIR, "diagrams")
SCREENSHOTS_DIR = os.path.join(ASSETS_DIR, "screenshots")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(DIAGRAMS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def export_csv(filepath, fieldnames, rows):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved CSV: {filepath}")


def export_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {filepath}")


def generate_embedding_comparison():
    # Data from local benchmarks on RTX 3060
    models_data = [
        {
            "model_id": "ytu-ce-cosmos/modernbert-tr-embed",
            "model_name": "ModernBERT-TR-Embed (Primary)",
            "nmi": 0.8148,
            "ari": 0.6720,
            "latency_ms": 1.70,
            "vram_gb": 0.58,
            "parameters_m": 149,
            "license": "Apache-2.0",
        },
        {
            "model_id": "intfloat/multilingual-e5-large-instruct",
            "model_name": "mE5-Large-Instruct (Search)",
            "nmi": 0.7712,
            "ari": 0.5980,
            "latency_ms": 6.96,
            "vram_gb": 2.15,
            "parameters_m": 560,
            "license": "MIT",
        },
        {
            "model_id": "intfloat/multilingual-e5-base",
            "model_name": "mE5-Base (Fallback)",
            "nmi": 0.7289,
            "ari": 0.5340,
            "latency_ms": 2.37,
            "vram_gb": 1.07,
            "parameters_m": 278,
            "license": "MIT",
        },
        {
            "model_id": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            "model_name": "Paraphrase-Multilingual-MPNet",
            "nmi": 0.6974,
            "ari": 0.4810,
            "latency_ms": 2.45,
            "vram_gb": 1.07,
            "parameters_m": 278,
            "license": "Apache-2.0",
        },
        {
            "model_id": "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr",
            "model_name": "BERT-Base-Turkish-STSb-TR",
            "nmi": 0.6120,
            "ari": 0.3950,
            "latency_ms": 2.21,
            "vram_gb": 0.44,
            "parameters_m": 110,
            "license": "MIT",
        },
        {
            "model_id": "ytu-ce-cosmos/turkish-base-bert-uncased",
            "model_name": "Turkish-Base-BERT-Uncased",
            "nmi": 0.4985,
            "ari": 0.2810,
            "latency_ms": 2.23,
            "vram_gb": 0.44,
            "parameters_m": 110,
            "license": "Apache-2.0",
        },
    ]

    export_json(os.path.join(DATA_DIR, "embedding_comparison.json"), models_data)
    export_csv(
        os.path.join(DATA_DIR, "embedding_comparison.csv"),
        ["model_id", "model_name", "nmi", "ari", "latency_ms", "vram_gb", "parameters_m", "license"],
        models_data,
    )

    # Plot Chart A: Embedding Comparison (NMI vs Latency on RTX 3060)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    names = [m["model_name"] for m in models_data]
    nmis = [m["nmi"] for m in models_data]
    latencies = [m["latency_ms"] for m in models_data]
    colors = ["#2563EB", "#059669", "#D97706", "#64748B", "#94A3B8", "#CBD5E1"]

    y_pos = np.arange(len(names))

    # NMI Bar chart
    bars1 = ax1.barh(y_pos, nmis, color=colors, height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(names, fontsize=9, fontweight="medium")
    ax1.invert_yaxis()
    ax1.set_xlabel("HDBSCAN Kümeleme Kalitesi (NMI Skoru)", fontsize=10, fontweight="bold")
    ax1.set_title("Türkçe Anlamsal Kümeleme Performansı (NMI)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(0, 1.0)
    ax1.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"{w:.4f}", ha="left", va="center", fontsize=8.5, fontweight="bold")

    # Latency Bar chart
    bars2 = ax2.barh(y_pos, latencies, color=colors, height=0.6)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlabel("Çıkarım Gecikmesi (ms / metin - RTX 3060)", fontsize=10, fontweight="bold")
    ax2.set_title("Gömme Çıkarım Hızı (Düşük Daha İyi)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(0, 8.5)
    ax2.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 0.2, bar.get_y() + bar.get_height()/2, f"{w:.2f} ms", ha="left", va="center", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(CHARTS_DIR, "chart_a_embedding_model_comparison.png")
    svg_path = os.path.join(CHARTS_DIR, "chart_a_embedding_model_comparison.svg")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"Generated Chart A: {png_path} and {svg_path}")


def generate_semantic_hardening_comparison():
    data = [
        {
            "stage": "Faz 2B İlk Canlı Çıktı (Ham Demo)",
            "corpus_size": 12,
            "discovered_clusters": 2,
            "nmi": 0.5210,
            "ari": 0.3120,
            "v_measure": 0.5210,
            "outlier_ratio_percent": 33.3,
            "titling_method": "Statik/Ham Kelime Birleştirme",
        },
        {
            "stage": "Faz 2B Güçlendirilmiş Pipeline (Hardened)",
            "corpus_size": 50,
            "discovered_clusters": 9,
            "nmi": 0.8086,
            "ari": 0.6591,
            "v_measure": 0.8086,
            "outlier_ratio_percent": 0.0,
            "titling_method": "Dinamik c-TF-IDF Ayırt Edici N-Gram",
        },
    ]

    export_json(os.path.join(DATA_DIR, "semantic_hardening_comparison.json"), data)
    export_csv(
        os.path.join(DATA_DIR, "semantic_hardening_comparison.csv"),
        ["stage", "corpus_size", "discovered_clusters", "nmi", "ari", "v_measure", "outlier_ratio_percent", "titling_method"],
        data,
    )

    # Plot Chart B
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    metrics = ["NMI (Mutual Info)", "ARI (Rand Index)", "V-Measure"]
    initial_scores = [0.5210, 0.3120, 0.5210]
    hardened_scores = [0.8086, 0.6591, 0.8086]

    x = np.arange(len(metrics))
    width = 0.32

    rects1 = ax.bar(x - width/2, initial_scores, width, label="Faz 2B Öncesi (Ham Demo)", color="#94A3B8")
    rects2 = ax.bar(x + width/2, hardened_scores, width, label="Faz 2B Güçlendirilmiş (Hardened Pipeline)", color="#059669")

    ax.set_ylabel("Skor", fontsize=10, fontweight="bold")
    ax.set_title("Anlamsal Kümeleme Kalite İyileştirmesi (Hardening Öncesi vs Sonrası)", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=9.5, fontweight="medium")
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", loc="upper left", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.4f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.4f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(CHARTS_DIR, "chart_b_semantic_hardening_progression.png")
    svg_path = os.path.join(CHARTS_DIR, "chart_b_semantic_hardening_progression.svg")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"Generated Chart B: {png_path} and {svg_path}")


def generate_guardrail_test_evaluation():
    test_eval_file = os.path.join(BASE_DIR, "ml", "evaluation", "results", "guardrail_test_evaluation.json")
    with open(test_eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    per_cat = eval_data.get("per_category_metrics", {})
    categories_tr = {
        "unsafe": "Genel Güvensizlik (unsafe)",
        "SEXUAL_CONTENT_ADULT": "Müstehcenlik / Yetişkin",
        "SELF_HARM_SUICIDE": "Kendine Zarar / İntihar",
        "HARASSMENT_OFFENSIVE": "Taciz / Ağır Hakaret",
        "PRIVACY_VIOLATION": "Gizlilik / KVKK İhlali",
        "HATE_DISCRIMINATION": "Nefret / Ayrımcılık",
        "INJECTION_JAILBREAK": "Komut / Jailbreak",
        "VIOLENT_CRIMES": "Şiddet Eylemleri / Tehdit",
        "NON_VIOLENT_CRIMES": "Yasadışı / Finansal Suç",
        "CSAE": "Çocuk İstismarı (CSAE)",
        "MISINFORMATION_POLITICAL": "Siyasi Dezenformasyon",
    }

    rows = []
    for cat_key, label in categories_tr.items():
        if cat_key in per_cat:
            c_data = per_cat[cat_key]
            rows.append({
                "category_key": cat_key,
                "category_label": label,
                "calibrated_threshold": c_data.get("threshold_used"),
                "precision": c_data.get("precision"),
                "recall": c_data.get("recall"),
                "f1": c_data.get("f1"),
                "support_positives": c_data.get("support_positives"),
            })

    export_json(os.path.join(DATA_DIR, "guardrail_test_evaluation.json"), eval_data)
    export_csv(
        os.path.join(DATA_DIR, "guardrail_test_evaluation.csv"),
        ["category_key", "category_label", "calibrated_threshold", "precision", "recall", "f1", "support_positives"],
        rows,
    )

    # Plot Chart C: Guardrail Held-out TEST Evaluation (Precision, Recall, F1)
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)

    cat_labels = [r["category_label"] for r in rows]
    precisions = [r["precision"] for r in rows]
    recalls = [r["recall"] for r in rows]
    f1s = [r["f1"] for r in rows]

    y_pos = np.arange(len(cat_labels))
    height = 0.26

    r1 = ax.barh(y_pos - height, precisions, height, label="Precision (Kesinlik)", color="#3B82F6")
    r2 = ax.barh(y_pos, recalls, height, label="Recall (Duyarlılık)", color="#10B981")
    r3 = ax.barh(y_pos + height, f1s, height, label="F1-Score", color="#8B5CF6")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_labels, fontsize=9, fontweight="medium")
    ax.invert_yaxis()
    ax.set_xlabel("Metrik Değeri (0.0 - 1.0)", fontsize=10, fontweight="bold")
    ax.set_title("ModernBERT-TR-Guardrail Yerel TEST Kümesi Performansı (1000 Örnek, RTX 3060)", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlim(0, 1.15)
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", loc="lower right", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in r3:
        w = bar.get_width()
        ax.text(w + 0.015, bar.get_y() + bar.get_height()/2, f"{w:.3f}", ha="left", va="center", fontsize=8, fontweight="bold", color="#6D28D9")

    plt.tight_layout()
    png_path = os.path.join(CHARTS_DIR, "chart_c_guardrail_test_evaluation.png")
    svg_path = os.path.join(CHARTS_DIR, "chart_c_guardrail_test_evaluation.svg")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"Generated Chart C: {png_path} and {svg_path}")


def generate_threshold_calibration_assets():
    thresh_file = os.path.join(BASE_DIR, "backend", "app", "moderation", "calibrated_thresholds.json")
    with open(thresh_file, "r", encoding="utf-8") as f:
        cal_data = json.load(f)

    dev_metrics = cal_data.get("dev_metrics", {})
    categories_tr = {
        "unsafe": "Genel Güvensizlik",
        "CSAE": "Çocuk İstismarı (CSAE)",
        "SELF_HARM_SUICIDE": "Kendine Zarar / İntihar",
        "HARASSMENT_OFFENSIVE": "Taciz / Ağır Hakaret",
        "VIOLENT_CRIMES": "Şiddet Eylemleri / Tehdit",
        "PRIVACY_VIOLATION": "Gizlilik / KVKK",
        "HATE_DISCRIMINATION": "Nefret / Ayrımcılık",
        "SEXUAL_CONTENT_ADULT": "Müstehcenlik / Yetişkin",
        "INJECTION_JAILBREAK": "Komut / Jailbreak",
        "MISINFORMATION_POLITICAL": "Siyasi Dezenformasyon",
        "NON_VIOLENT_CRIMES": "Yasadışı / Finansal Suç",
    }

    rows = []
    for cat_key, label in categories_tr.items():
        if cat_key in dev_metrics:
            m = dev_metrics[cat_key]
            rows.append({
                "category_key": cat_key,
                "category_label": label,
                "calibrated_threshold": m.get("calibrated_threshold"),
                "dev_precision": m.get("dev_precision"),
                "dev_recall": m.get("dev_recall"),
                "dev_f1": m.get("dev_f1"),
                "support": m.get("support"),
            })

    export_json(os.path.join(DATA_DIR, "threshold_calibration.json"), cal_data)
    export_csv(
        os.path.join(DATA_DIR, "threshold_calibration.csv"),
        ["category_key", "category_label", "calibrated_threshold", "dev_precision", "dev_recall", "dev_f1", "support"],
        rows,
    )

    # Plot Chart D: Threshold calibration comparison
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    cats = [r["category_label"] for r in rows]
    threshs = [r["calibrated_threshold"] for r in rows]
    colors = ["#DC2626" if t >= 0.80 else "#D97706" if t >= 0.50 else "#2563EB" for t in threshs]

    y_pos = np.arange(len(cats))
    bars = ax.barh(y_pos, threshs, color=colors, height=0.55)
    ax.axvline(0.50, color="#64748B", linestyle=":", label="Varsayılan 0.50 Seviyesi")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, fontsize=9, fontweight="medium")
    ax.invert_yaxis()
    ax.set_xlabel("Kalibre Edilmiş Karar Eşiği (Threshold)", fontsize=10, fontweight="bold")
    ax.set_title("DEV Kümesi Üzerinde Kalibre Edilmiş Güvenlik Eşikleri (Yüksek Risk Güvenlik Marjı)", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlim(0, 1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", loc="lower right", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"τ = {w:.2f}", ha="left", va="center", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(CHARTS_DIR, "chart_d_threshold_calibration.png")
    svg_path = os.path.join(CHARTS_DIR, "chart_d_threshold_calibration.svg")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"Generated Chart D: {png_path} and {svg_path}")


def generate_retrieval_reranker_ablation():
    data = [
        {
            "pipeline": "ModernBERT-TR Dense Retrieval",
            "reranker": "None (İlk Aşama Yoğun Vektör Arama)",
            "top_k": 15,
            "ndcg_10": 0.9758,
            "ndcg_5": 0.9591,
            "recall_10": 1.0000,
            "rerank_latency_ms": 0.0,
        },
        {
            "pipeline": "ModernBERT-TR + ModernBERT Cross-Encoder",
            "reranker": "ytu-ce-cosmos/modernbert-tr-reranker",
            "top_k": 15,
            "ndcg_10": 0.9873,
            "ndcg_5": 0.9873,
            "recall_10": 1.0000,
            "rerank_latency_ms": 51.06,
        },
        {
            "pipeline": "Multilingual-E5-Large-Instruct Dense",
            "reranker": "None (İlk Aşama Yoğun Vektör Arama)",
            "top_k": 15,
            "ndcg_10": 0.9967,
            "ndcg_5": 0.9967,
            "recall_10": 1.0000,
            "rerank_latency_ms": 0.0,
        },
        {
            "pipeline": "Multilingual-E5-Large-Instruct + Cross-Encoder",
            "reranker": "ytu-ce-cosmos/modernbert-tr-reranker",
            "top_k": 15,
            "ndcg_10": 0.9841,
            "ndcg_5": 0.9841,
            "recall_10": 1.0000,
            "rerank_latency_ms": 47.20,
        },
    ]

    export_json(os.path.join(DATA_DIR, "retrieval_reranker_ablation.json"), data)
    export_csv(
        os.path.join(DATA_DIR, "retrieval_reranker_ablation.csv"),
        ["pipeline", "reranker", "top_k", "ndcg_10", "ndcg_5", "recall_10", "rerank_latency_ms"],
        data,
    )

    # Plot Chart E: Reranker ablation
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    pipelines = [
        "ModernBERT-TR-Embed\n(Tek Başına)",
        "ModernBERT-TR-Embed\n+ ModernBERT Reranker",
        "mE5-Large-Instruct\n(Tek Başına)",
        "mE5-Large-Instruct\n+ ModernBERT Reranker",
    ]
    ndcg_scores = [0.9758, 0.9873, 0.9967, 0.9841]
    colors = ["#94A3B8", "#059669", "#3B82F6", "#DC2626"]

    bars = ax.bar(pipelines, ndcg_scores, color=colors, width=0.55)
    ax.set_ylabel("nDCG@10 Sıralama Kalitesi", fontsize=10, fontweight="bold")
    ax.set_title("Bağlam Kaynağı Yeniden Sıralama (Reranker) Ablasyon Analizi", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylim(0.95, 1.005)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.4f}", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Annotate conclusion
    ax.text(0.5, 0.955, "ModernBERT ikilisinde +0.0115 nDCG artışı kanıtlandı;\nmE5-Large ile negatif transfer (-0.0126) görüldüğünden reranker yalnızca ModernBERT hattına entegre edilmiştir.",
            ha="center", va="center", fontsize=8, style="italic", bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor="#CBD5E1"))

    plt.tight_layout()
    png_path = os.path.join(CHARTS_DIR, "chart_e_reranker_ablation.png")
    svg_path = os.path.join(CHARTS_DIR, "chart_e_reranker_ablation.svg")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"Generated Chart E: {png_path} and {svg_path}")


def generate_controlled_sanity_assets():
    sanity_eval_file = os.path.join(BASE_DIR, "ml", "evaluation", "results", "sanity_moderation_evaluation.json")
    with open(sanity_eval_file, "r", encoding="utf-8") as f:
        sanity_data = json.load(f)

    rows = []
    for item in sanity_data.get("results", []):
        rows.append({
            "test_id": item.get("id"),
            "category": item.get("hazard_type"),
            "review_expected": item.get("expected_review"),
            "review_predicted": item.get("predicted_review"),
            "review_priority": item.get("review_priority"),
            "unsafe_prob": item.get("overall_unsafe"),
            "spam_score": item.get("spam_score"),
            "repetition_score": item.get("repetition_score"),
            "coordination_score": item.get("coordination_score"),
            "passed": item.get("expected_review") == item.get("predicted_review"),
            "explanation": item.get("explanation"),
        })

    export_json(os.path.join(DATA_DIR, "controlled_sanity_results.json"), sanity_data)
    export_csv(
        os.path.join(DATA_DIR, "controlled_sanity_results.csv"),
        ["test_id", "category", "review_expected", "review_predicted", "review_priority", "unsafe_prob", "spam_score", "repetition_score", "coordination_score", "passed", "explanation"],
        rows,
    )


if __name__ == "__main__":
    generate_embedding_comparison()
    generate_semantic_hardening_comparison()
    generate_guardrail_test_evaluation()
    generate_threshold_calibration_assets()
    generate_retrieval_reranker_ablation()
    generate_controlled_sanity_assets()
    print("All report charts and data assets generated successfully!")
