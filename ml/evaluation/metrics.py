import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


def cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarities between matrices a and b."""
    # Ensure vectors are normalized
    norm_a = np.linalg.norm(a, axis=1, keepdims=True)
    norm_b = np.linalg.norm(b, axis=1, keepdims=True)
    norm_a = np.where(norm_a == 0, 1e-12, norm_a)
    norm_b = np.where(norm_b == 0, 1e-12, norm_b)
    a_norm = a / norm_a
    b_norm = b / norm_b
    return np.dot(a_norm, b_norm.T)


def compute_spearman_rho(x: List[float], y: List[float]) -> float:
    """Compute Spearman's rank correlation coefficient between two 1D sequences."""
    n = len(x)
    if n < 2:
        return 0.0

    def get_ranks(seq: List[float]) -> List[float]:
        indexed = sorted(enumerate(seq), key=lambda item: item[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j][1] == indexed[j + 1][1]:
                j += 1
            avg_rank = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rank_x = np.array(get_ranks(x))
    rank_y = np.array(get_ranks(y))

    # Pearson correlation on ranks
    std_x = np.std(rank_x)
    std_y = np.std(rank_y)
    if std_x == 0 or std_y == 0:
        return 0.0
    cov = np.mean((rank_x - np.mean(rank_x)) * (rank_y - np.mean(rank_y)))
    return float(cov / (std_x * std_y))


def compute_pearson_r(x: List[float], y: List[float]) -> float:
    """Compute Pearson correlation coefficient."""
    arr_x = np.array(x)
    arr_y = np.array(y)
    std_x = np.std(arr_x)
    std_y = np.std(arr_y)
    if std_x == 0 or std_y == 0:
        return 0.0
    cov = np.mean((arr_x - np.mean(arr_x)) * (arr_y - np.mean(arr_y)))
    return float(cov / (std_x * std_y))


def evaluate_sts_pairs(
    embeddings_a: np.ndarray,
    embeddings_b: np.ndarray,
    gold_scores: List[float],
) -> Dict[str, float]:
    """Evaluate STS semantic similarity pairs against ground truth human scores."""
    # Compute cosine similarity for each pair
    dot_products = np.sum(embeddings_a * embeddings_b, axis=1)
    norm_a = np.linalg.norm(embeddings_a, axis=1)
    norm_b = np.linalg.norm(embeddings_b, axis=1)
    cosine_sims = dot_products / (np.maximum(norm_a * norm_b, 1e-12))
    cosine_sims = [float(cs) for cs in cosine_sims]

    spearman_rho = compute_spearman_rho(cosine_sims, gold_scores)
    pearson_r = compute_pearson_r(cosine_sims, gold_scores)

    return {
        "spearman_rho": round(spearman_rho, 4),
        "pearson_r": round(pearson_r, 4),
        "pair_count": len(gold_scores),
    }


def evaluate_retrieval(
    query_embeddings: np.ndarray,
    corpus_embeddings: np.ndarray,
    qrels: Dict[int, List[int]],
    k_values: Tuple[int, ...] = (1, 5, 10),
) -> Dict[str, float]:
    """Evaluate Information Retrieval metrics: nDCG@K, MRR@10, Recall@K."""
    sim_matrix = cosine_similarity_matrix(query_embeddings, corpus_embeddings)
    num_queries = len(qrels)

    ndcg_scores = {k: 0.0 for k in k_values}
    recall_scores = {k: 0.0 for k in k_values}
    mrr_scores = {k: 0.0 for k in k_values}

    for q_idx, relevant_docs in qrels.items():
        if q_idx >= len(sim_matrix):
            continue
        scores = sim_matrix[q_idx]
        ranked_doc_indices = np.argsort(-scores)

        target_set = set(relevant_docs)

        # MRR@10
        mrr_found = False
        for rank, doc_id in enumerate(ranked_doc_indices[:10]):
            if doc_id in target_set and not mrr_found:
                mrr_scores[10] += 1.0 / (rank + 1)
                mrr_found = True

        # Recall and nDCG at each K
        for k in k_values:
            top_k = ranked_doc_indices[:k]
            hits = sum(1 for doc_id in top_k if doc_id in target_set)
            recall_scores[k] += hits / max(1, len(target_set))

            # DCG@K
            dcg = 0.0
            for rank, doc_id in enumerate(top_k):
                rel = 1.0 if doc_id in target_set else 0.0
                dcg += rel / math.log2(rank + 2)

            # IDCG@K
            ideal_hits = min(k, len(target_set))
            idcg = sum(1.0 / math.log2(r + 2) for r in range(ideal_hits))

            ndcg = (dcg / idcg) if idcg > 0 else 0.0
            ndcg_scores[k] += ndcg

    results: Dict[str, float] = {}
    for k in k_values:
        results[f"ndcg@{k}"] = round(ndcg_scores[k] / max(1, num_queries), 4)
        results[f"recall@{k}"] = round(recall_scores[k] / max(1, num_queries), 4)

    results["mrr@10"] = round(mrr_scores[10] / max(1, num_queries), 4)
    results["query_count"] = num_queries
    return results


def evaluate_clustering(
    true_labels: List[Union[int, str]],
    pred_labels: List[int],
    embeddings: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Compute clustering metrics: NMI, ARI, V-measure, and noise ratio."""
    # Convert labels to integer IDs
    unique_true = {lbl: i for i, lbl in enumerate(set(true_labels))}
    y_true = np.array([unique_true[lbl] for lbl in true_labels])
    y_pred = np.array(pred_labels)

    # Filter noise (-1 in HDBSCAN) for pure cluster quality metrics, but track noise ratio
    noise_mask = y_pred == -1
    noise_count = int(np.sum(noise_mask))
    noise_ratio = noise_count / len(y_pred) if len(y_pred) > 0 else 0.0

    valid_mask = ~noise_mask
    if np.sum(valid_mask) < 2:
        return {
            "nmi": 0.0,
            "ari": 0.0,
            "v_measure": 0.0,
            "discovered_clusters": len(set(pred_labels) - {-1}),
            "noise_ratio": round(noise_ratio, 4),
        }

    try:
        from sklearn.metrics import (
            adjusted_rand_score,
            normalized_mutual_info_score,
            v_measure_score,
            silhouette_score,
        )

        nmi = float(normalized_mutual_info_score(y_true[valid_mask], y_pred[valid_mask]))
        ari = float(adjusted_rand_score(y_true[valid_mask], y_pred[valid_mask]))
        v_meas = float(v_measure_score(y_true[valid_mask], y_pred[valid_mask]))

        sil = 0.0
        if embeddings is not None and len(set(y_pred[valid_mask])) > 1:
            try:
                sil = float(
                    silhouette_score(
                        embeddings[valid_mask], y_pred[valid_mask], metric="cosine"
                    )
                )
            except Exception:
                sil = 0.0

        return {
            "nmi": round(nmi, 4),
            "ari": round(ari, 4),
            "v_measure": round(v_meas, 4),
            "silhouette_cosine": round(sil, 4),
            "discovered_clusters": len(set(pred_labels) - {-1}),
            "noise_ratio": round(noise_ratio, 4),
            "sample_count": len(y_true),
        }
    except ImportError:
        # Fallback pure-python calculation if sklearn not yet loaded
        return {
            "nmi": 0.0,
            "ari": 0.0,
            "v_measure": 0.0,
            "discovered_clusters": len(set(pred_labels) - {-1}),
            "noise_ratio": round(noise_ratio, 4),
            "sample_count": len(y_true),
        }
