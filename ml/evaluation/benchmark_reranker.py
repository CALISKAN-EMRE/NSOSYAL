import gc
import json
import os
import sys
import time
import numpy as np
import torch
from pathlib import Path

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sentence_transformers import CrossEncoder, SentenceTransformer
from ml.embeddings.hf_provider import HuggingFaceEmbeddingProvider
from ml.evaluation.metrics import evaluate_retrieval


def benchmark_reranker_pipeline(top_k: int = 15):
    dataset_path = repo_root / "ml" / "evaluation" / "datasets" / "social_eval_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    corpus_items = data["retrieval_benchmark"]["corpus"]
    queries_items = data["retrieval_benchmark"]["queries"]

    corpus_texts = [item["text"] for item in corpus_items]
    query_texts = [item["query"] for item in queries_items]
    doc_id_to_idx = {item["doc_id"]: idx for idx, item in enumerate(corpus_items)}

    qrels = {}
    for q_idx, item in enumerate(queries_items):
        target_indices = [
            doc_id_to_idx[d_id] for d_id in item["relevant_docs"] if d_id in doc_id_to_idx
        ]
        qrels[q_idx] = target_indices

    dense_models = [
        "ytu-ce-cosmos/modernbert-tr-embed",
        "intfloat/multilingual-e5-large-instruct",
    ]

    reranker_model_id = "ytu-ce-cosmos/modernbert-tr-reranker"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=================================================================")
    print("  NSOSYAL PUSULA — TWO-STAGE RETRIEVAL & RERANKING BENCHMARK     ")
    print(f"  Reranker: {reranker_model_id} (Device: {device}, Top-K: {top_k})")
    print("=================================================================")

    # Load Reranker
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    t_rerank_load = time.perf_counter()
    reranker = CrossEncoder(reranker_model_id, device=device)
    rerank_load_time = time.perf_counter() - t_rerank_load

    reranker_vram_gb = (
        torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0.0
    )
    reranker_peak_vram_gb = (
        torch.cuda.max_memory_allocated() / (1024**3)
        if torch.cuda.is_available()
        else 0.0
    )

    results = {
        "reranker_metadata": {
            "model_id": reranker_model_id,
            "architecture": "ModernBERT Cross-Encoder",
            "device": device,
            "top_k_candidates": top_k,
            "reranker_vram_allocated_gb": round(reranker_vram_gb, 2),
            "reranker_peak_vram_gb": round(reranker_peak_vram_gb, 2),
            "load_time_sec": round(rerank_load_time, 2),
        },
        "experiments": {},
    }

    for dense_model_id in dense_models:
        print(f"\n>>> Running Pipeline: Dense [{dense_model_id}] + Cross-Encoder [{reranker_model_id}]")
        provider = HuggingFaceEmbeddingProvider(dense_model_id, device=device)

        corpus_embs = provider.encode_documents(corpus_texts)
        query_embs = provider.encode_queries(query_texts)

        # 1. Initial Dense Retrieval
        sim_matrix = np.dot(query_embs, corpus_embs.T)

        # Baseline Dense Metrics
        dense_metrics = evaluate_retrieval(
            query_embeddings=query_embs,
            corpus_embeddings=corpus_embs,
            qrels=qrels,
            k_values=(1, 5, 10),
        )

        # 2. Rerank Top-K Candidates with Cross-Encoder
        t_rerank_start = time.perf_counter()
        reranked_sim_matrix = np.copy(sim_matrix)

        for q_idx, q_text in enumerate(query_texts):
            top_k_indices = np.argsort(-sim_matrix[q_idx])[:top_k]
            candidate_pairs = [(q_text, corpus_texts[doc_idx]) for doc_idx in top_k_indices]

            # Predict cross-encoder scores
            ce_scores = reranker.predict(candidate_pairs, show_progress_bar=False)

            # Assign reranked scores to the matrix for metric evaluation
            # Set unselected to very low score to preserve relative ranking outside top-k
            reranked_sim_matrix[q_idx, :] = -1e9
            for idx_in_top, doc_idx in enumerate(top_k_indices):
                reranked_sim_matrix[q_idx, doc_idx] = ce_scores[idx_in_top]

        total_rerank_time = time.perf_counter() - t_rerank_start
        avg_rerank_ms_per_query = (total_rerank_time / len(query_texts)) * 1000.0

        # Evaluate Reranked Metrics
        # Re-compute metric with reranked_sim_matrix
        num_queries = len(qrels)
        ndcg_scores = {1: 0.0, 5: 0.0, 10: 0.0}
        mrr_scores = {10: 0.0}
        recall_scores = {1: 0.0, 5: 0.0, 10: 0.0}

        import math

        for q_idx, target_indices in qrels.items():
            scores = reranked_sim_matrix[q_idx]
            ranked_doc_indices = np.argsort(-scores)
            target_set = set(target_indices)

            mrr_found = False
            for rank, doc_id in enumerate(ranked_doc_indices[:10]):
                if doc_id in target_set and not mrr_found:
                    mrr_scores[10] += 1.0 / (rank + 1)
                    mrr_found = True

            for k in (1, 5, 10):
                top_k_docs = ranked_doc_indices[:k]
                hits = sum(1 for doc_id in top_k_docs if doc_id in target_set)
                recall_scores[k] += hits / max(1, len(target_set))

                dcg = sum(
                    (1.0 if doc_id in target_set else 0.0) / math.log2(rank + 2)
                    for rank, doc_id in enumerate(top_k_docs)
                )
                ideal_hits = min(k, len(target_set))
                idcg = sum(1.0 / math.log2(r + 2) for r in range(ideal_hits))
                ndcg = (dcg / idcg) if idcg > 0 else 0.0
                ndcg_scores[k] += ndcg

        reranked_metrics = {
            "ndcg@1": round(ndcg_scores[1] / num_queries, 4),
            "ndcg@5": round(ndcg_scores[5] / num_queries, 4),
            "ndcg@10": round(ndcg_scores[10] / num_queries, 4),
            "mrr@10": round(mrr_scores[10] / num_queries, 4),
            "recall@10": round(recall_scores[10] / num_queries, 4),
            "reranking_latency_ms_per_query": round(avg_rerank_ms_per_query, 2),
        }

        print(f"  [Before Reranking] nDCG@10: {dense_metrics['ndcg@10']}, MRR@10: {dense_metrics['mrr@10']}, Recall@10: {dense_metrics['recall@10']}")
        print(f"  [After Reranking]  nDCG@10: {reranked_metrics['ndcg@10']}, MRR@10: {reranked_metrics['mrr@10']}, Recall@10: {reranked_metrics['recall@10']}")
        print(f"  Reranking Latency: {reranked_metrics['reranking_latency_ms_per_query']} ms/query (for {top_k} candidates)")

        results["experiments"][dense_model_id] = {
            "dense_before": dense_metrics,
            "reranked_after": reranked_metrics,
            "ndcg_delta": round(reranked_metrics["ndcg@10"] - dense_metrics["ndcg@10"], 4),
        }

        del provider
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Save reranker results
    out_file = repo_root / "ml" / "reports" / "reranker_benchmark_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nReranker benchmark results saved to: {out_file}")
    return results


if __name__ == "__main__":
    benchmark_reranker_pipeline(top_k=15)
