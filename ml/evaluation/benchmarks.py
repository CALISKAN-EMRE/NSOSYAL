import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from ml.embeddings.base import EmbeddingProvider
from ml.evaluation.metrics import (
    evaluate_clustering,
    evaluate_retrieval,
    evaluate_sts_pairs,
)
from ml.clustering.clusterers import (
    DeterministicKMeansClusterer,
    HDBSCANClusterer,
    OracleMetadataGroupingBaseline,
    RandomClusterer,
    TfIdfSphericalKMeansClusterer,
)


class BenchmarkRunner:
    """Orchestrates comprehensive embedding model benchmarks for NSosyal Pusula."""

    def __init__(self, dataset_path: Optional[str] = None):
        if dataset_path is None:
            dataset_path = str(
                Path(__file__).resolve().parent / "datasets" / "social_eval_dataset.json"
            )
        self.dataset_path = Path(dataset_path)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_sts_benchmark(
        self, provider: EmbeddingProvider, split: str = "test"
    ) -> Dict[str, Any]:
        """Run STS semantic similarity benchmark for a provider on the chosen split."""
        pairs = self.data["sts_pairs"].get(split, [])
        if not pairs:
            return {"error": f"Split '{split}' not found"}

        sentences_a = [p["sentence_a"] for p in pairs]
        sentences_b = [p["sentence_b"] for p in pairs]
        gold_scores = [p["gold_score"] for p in pairs]

        emb_a = provider.encode_documents(sentences_a)
        emb_b = provider.encode_documents(sentences_b)

        metrics = evaluate_sts_pairs(emb_a, emb_b, gold_scores)
        metrics["split"] = split
        metrics["pair_count"] = len(pairs)
        return metrics

    def run_clustering_benchmark(self, provider: EmbeddingProvider) -> Dict[str, Any]:
        """Run clustering evaluation on Turkish social media clustering corpus."""
        corpus = self.data["clustering_corpus"]
        texts = [item["text"] for item in corpus]
        true_labels = [item["cluster_label"] for item in corpus]
        n_clusters = len(set(true_labels))

        embeddings = provider.encode_documents(texts)

        # 1. Evaluate with HDBSCAN
        hdbscan_clusterer = HDBSCANClusterer(min_cluster_size=3)
        hdbscan_preds = hdbscan_clusterer.fit_predict(embeddings)
        hdbscan_metrics = evaluate_clustering(true_labels, hdbscan_preds, embeddings)

        # 2. Evaluate with Deterministic K-Means (k=6)
        kmeans_clusterer = DeterministicKMeansClusterer(n_clusters=n_clusters, random_state=42)
        kmeans_preds = kmeans_clusterer.fit_predict(embeddings)
        kmeans_metrics = evaluate_clustering(true_labels, kmeans_preds, embeddings)

        return {
            "hdbscan": hdbscan_metrics,
            "kmeans": kmeans_metrics,
            "corpus_size": len(texts),
            "ground_truth_clusters": n_clusters,
        }

    def run_retrieval_benchmark(self, provider: EmbeddingProvider) -> Dict[str, Any]:
        """Run Information Retrieval benchmark with hard negatives."""
        corpus_items = self.data["retrieval_benchmark"]["corpus"]
        queries_items = self.data["retrieval_benchmark"]["queries"]

        corpus_texts = [item["text"] for item in corpus_items]
        query_texts = [item["query"] for item in queries_items]
        doc_id_to_idx = {item["doc_id"]: idx for idx, item in enumerate(corpus_items)}

        qrels = {}
        for q_idx, item in enumerate(queries_items):
            target_indices = [
                doc_id_to_idx[d_id] for d_id in item["relevant_docs"] if d_id in doc_id_to_idx
            ]
            qrels[q_idx] = target_indices

        corpus_embeddings = provider.encode_documents(corpus_texts)
        query_embeddings = provider.encode_queries(query_texts)

        metrics = evaluate_retrieval(
            query_embeddings=query_embeddings,
            corpus_embeddings=corpus_embeddings,
            qrels=qrels,
            k_values=(1, 5, 10),
        )
        metrics["query_count"] = len(queries_items)
        metrics["corpus_count"] = len(corpus_items)
        return metrics

    def measure_latency_and_throughput(
        self, provider: EmbeddingProvider, test_sentence: str, iterations: int = 30
    ) -> Dict[str, Any]:
        """Benchmark encoding latency per sentence."""
        # Warmup
        _ = provider.encode_documents([test_sentence])

        start_time = time.perf_counter()
        for _ in range(iterations):
            _ = provider.encode_documents([test_sentence])
        total_time = time.perf_counter() - start_time

        avg_latency_ms = (total_time / iterations) * 1000.0
        return {
            "avg_latency_ms_per_sentence": round(avg_latency_ms, 2),
            "throughput_sentences_per_sec": round(1000.0 / max(0.001, avg_latency_ms), 1),
            "iterations": iterations,
        }

    def evaluate_model(self, provider: EmbeddingProvider) -> Dict[str, Any]:
        """Run full evaluation suite for a single provider."""
        metadata = provider.model_metadata()

        sts_dev = self.run_sts_benchmark(provider, split="dev")
        sts_test = self.run_sts_benchmark(provider, split="test")
        clustering = self.run_clustering_benchmark(provider)
        retrieval = self.run_retrieval_benchmark(provider)

        test_sentence = (
            "Yapay zekâ ve açık kaynak yazılımlar üniversitelerde yeni bir eğitim modeli başlatıyor."
        )
        latency = self.measure_latency_and_throughput(provider, test_sentence)

        return {
            "metadata": metadata,
            "sts_evaluation": {
                "dev": sts_dev,
                "test": sts_test,
            },
            "clustering_evaluation": clustering,
            "retrieval_evaluation": retrieval,
            "performance": latency,
        }

    def evaluate_baselines(self) -> Dict[str, Any]:
        """Evaluate both unsupervised (TF-IDF, Random) and supervised oracle baselines."""
        corpus = self.data["clustering_corpus"]
        texts = [item["text"] for item in corpus]
        true_labels = [item["cluster_label"] for item in corpus]
        n_clusters = len(set(true_labels))

        # 1. Unsupervised TF-IDF + Spherical K-Means
        tfidf_clusterer = TfIdfSphericalKMeansClusterer(n_clusters=n_clusters, random_state=42)
        tfidf_preds = tfidf_clusterer.fit_predict_texts(texts)
        tfidf_metrics = evaluate_clustering(true_labels, tfidf_preds)

        # 2. Random Chance Baseline
        random_clusterer = RandomClusterer(n_clusters=n_clusters, random_state=42)
        random_preds = random_clusterer.fit_predict(len(texts))
        random_metrics = evaluate_clustering(true_labels, random_preds)

        # 3. Supervised Oracle Metadata Baseline (Upper Bound Reference Only)
        oracle_clusterer = OracleMetadataGroupingBaseline()
        oracle_preds = oracle_clusterer.predict_texts(texts)
        oracle_metrics = evaluate_clustering(true_labels, oracle_preds)

        return {
            "tfidf_kmeans_unsupervised": {
                "description": "Label-blind baseline: TF-IDF Bag-of-Words + Spherical K-Means (k=6)",
                "clustering": tfidf_metrics,
            },
            "random_baseline": {
                "description": "Lower-bound chance baseline: Random uniform cluster assignment",
                "clustering": random_metrics,
            },
            "oracle_metadata_grouping": {
                "description": "SUPERVISED ORACLE REFERENCE: Regex keyword mapping directly derived from topic labels (Upper Bound)",
                "clustering": oracle_metrics,
            },
        }
