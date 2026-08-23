from collections import Counter
import re
from typing import Any, Dict, List, Optional
import numpy as np

from app.ml.base import BaseClusterService, BaseEmbeddingService, SemanticCluster


class SemanticClusterService(BaseClusterService):
    """Production semantic clustering using ModernBERT-TR embeddings + HDBSCAN."""

    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        min_cluster_size: int = 3,
        min_samples: Optional[int] = 2,
    ):
        self.embedding_service = embedding_service
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples

    def cluster_posts(self, posts: List[Any]) -> List[SemanticCluster]:
        """Cluster a collection of Post objects into semantic groups."""
        if not posts:
            return []

        if len(posts) < self.min_cluster_size:
            # Fallback if too few posts: single cluster
            return [
                SemanticCluster(
                    cluster_id="semantic-cluster-all",
                    label=self._derive_cluster_label([p.text for p in posts]),
                    post_ids=[p.id for p in posts],
                    confidence_score=1.0,
                    key_themes=self._extract_key_themes(posts),
                    representative_post_ids=[posts[0].id] if posts else [],
                    is_noise=False,
                )
            ]

        texts = [p.text for p in posts]
        embeddings = self.embedding_service.encode_documents(texts)

        # Normalize to unit hypersphere for cosine distance equivalence
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        normed_embeddings = embeddings / norms

        # HDBSCAN clustering
        labels, probabilities = self._run_hdbscan(normed_embeddings)

        # Group posts by cluster label
        clusters_dict: Dict[int, List[int]] = {}
        for idx, lbl in enumerate(labels):
            clusters_dict.setdefault(lbl, []).append(idx)

        # Calculate centroids for non-noise clusters
        centroids: Dict[int, np.ndarray] = {}
        for lbl, member_indices in clusters_dict.items():
            if lbl != -1 and member_indices:
                cent = np.mean(normed_embeddings[member_indices], axis=0)
                cent = cent / (np.linalg.norm(cent) + 1e-12)
                centroids[lbl] = cent

        # Handle noise points (-1) by reassigning to closest centroid if similarity > 0.60
        if -1 in clusters_dict and centroids:
            noise_indices = list(clusters_dict[-1])
            unassigned_noise = []
            for n_idx in noise_indices:
                n_vec = normed_embeddings[n_idx]
                best_lbl = None
                best_sim = -1.0
                for c_lbl, cent in centroids.items():
                    sim = float(np.dot(n_vec, cent))
                    if sim > best_sim:
                        best_sim = sim
                        best_lbl = c_lbl

                if best_lbl is not None and best_sim >= 0.60:
                    clusters_dict[best_lbl].append(n_idx)
                else:
                    unassigned_noise.append(n_idx)

            if unassigned_noise:
                clusters_dict[-1] = unassigned_noise
            else:
                del clusters_dict[-1]

        # Assemble SemanticCluster models
        result_clusters: List[SemanticCluster] = []
        cluster_counter = 1

        # Sort clusters by size descending
        sorted_labels = sorted(
            [l for l in clusters_dict.keys() if l != -1],
            key=lambda l: len(clusters_dict[l]),
            reverse=True,
        )

        for lbl in sorted_labels:
            indices = clusters_dict[lbl]
            cluster_posts = [posts[i] for i in indices]
            cluster_embs = normed_embeddings[indices]
            centroid = centroids.get(lbl, np.mean(cluster_embs, axis=0))

            # Find exemplar posts (closest cosine similarity to centroid)
            sims = np.dot(cluster_embs, centroid)
            exemplar_sorted_indices = [indices[i] for i in np.argsort(-sims)]
            representative_ids = [posts[i].id for i in exemplar_sorted_indices[:3]]

            # Average membership probability
            cluster_probs = [probabilities[i] for i in indices if i < len(probabilities)]
            avg_conf = float(np.mean(cluster_probs)) if cluster_probs else 0.85

            cluster_id = f"semantic-cluster-{cluster_counter}"
            cluster_label = self._derive_cluster_label([p.text for p in cluster_posts])
            key_themes = self._extract_key_themes(cluster_posts)

            result_clusters.append(
                SemanticCluster(
                    cluster_id=cluster_id,
                    label=cluster_label,
                    post_ids=[p.id for p in cluster_posts],
                    confidence_score=round(max(0.5, min(1.0, avg_conf)), 3),
                    key_themes=key_themes,
                    representative_post_ids=representative_ids,
                    is_noise=False,
                )
            )
            cluster_counter += 1

        # Add noise cluster if remaining
        if -1 in clusters_dict and clusters_dict[-1]:
            noise_posts = [posts[i] for i in clusters_dict[-1]]
            result_clusters.append(
                SemanticCluster(
                    cluster_id="semantic-cluster-outliers",
                    label="Diğer & Ayrık Konular (Outliers)",
                    post_ids=[p.id for p in noise_posts],
                    confidence_score=0.35,
                    key_themes=self._extract_key_themes(noise_posts),
                    representative_post_ids=[p.id for p in noise_posts[:2]],
                    is_noise=True,
                )
            )

        return result_clusters

    def _run_hdbscan(self, normed_embeddings: np.ndarray) -> tuple:
        """Run HDBSCAN on normalized vectors."""
        try:
            from sklearn.cluster import HDBSCAN

            clusterer = HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(normed_embeddings)
            probabilities = getattr(
                clusterer, "probabilities_", np.ones(len(normed_embeddings), dtype=float)
            )
            return labels, probabilities
        except Exception:
            # Distance-threshold fallback if HDBSCAN package issues occur
            n_samples = len(normed_embeddings)
            labels = -np.ones(n_samples, dtype=int)
            sim_mat = np.dot(normed_embeddings, normed_embeddings.T)
            visited = set()
            c_id = 0
            for i in range(n_samples):
                if i in visited:
                    continue
                nbrs = [j for j in range(n_samples) if sim_mat[i, j] >= 0.72]
                if len(nbrs) >= self.min_cluster_size:
                    for n in nbrs:
                        labels[n] = c_id
                        visited.add(n)
                    c_id += 1
            return labels, np.ones(n_samples, dtype=float) * 0.85

    def _extract_key_themes(self, posts: List[Any]) -> List[str]:
        """Extract dominant keyphrases / tags from cluster posts."""
        all_tags = []
        for p in posts:
            if hasattr(p, "tags") and p.tags:
                all_tags.extend(p.tags)

        if all_tags:
            counts = Counter(all_tags)
            return [tag for tag, _ in counts.most_common(6)]

        # Fallback to word frequencies if no tags
        words = []
        stopwords = {
            "ve", "ile", "bir", "bu", "için", "de", "da", "çok", "daha", "en",
            "olan", "olarak", "gibi", "kadar", "sonra", "önce", "yeni", "tüm",
        }
        for p in posts:
            clean = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", p.text.lower())
            words.extend([w for w in clean if w not in stopwords])

        counts = Counter(words)
        return [w.capitalize() for w, _ in counts.most_common(5)] or ["Genel Tartışma"]

    def _derive_cluster_label(self, texts: List[str]) -> str:
        """Derive a concise descriptive title for the cluster."""
        stopwords = {
            "ve", "ile", "bir", "bu", "için", "de", "da", "çok", "daha", "en",
            "olan", "olarak", "gibi", "kadar", "sonra", "önce", "yeni", "tüm", "ne",
            "var", "yok", "her", "ama", "fakat", "çünkü", "nasıl", "neden", "şöyle",
        }
        words = []
        for t in texts:
            clean = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", t.lower())
            words.extend([w for w in clean if w not in stopwords])

        top_words = [w.capitalize() for w, _ in Counter(words).most_common(3)]
        if top_words:
            return " & ".join(top_words)
        return "Semantik Tartışma Grubu"


class DemoClusterService(BaseClusterService):
    """Deterministic cluster service for demo mode / testing."""

    def __init__(self):
        pass

    def cluster_posts(self, posts: List[Any]) -> List[SemanticCluster]:
        if not posts:
            return []

        # Group by topic_id if available, or simple partition
        groups: Dict[str, List[Any]] = {}
        for p in posts:
            t_id = getattr(p, "topic_id", "genel")
            groups.setdefault(t_id, []).append(p)

        clusters = []
        for idx, (t_id, group_posts) in enumerate(groups.items(), 1):
            title = getattr(group_posts[0], "topic_title", t_id.replace("-", " ").title())
            clusters.append(
                SemanticCluster(
                    cluster_id=f"demo-cluster-{idx}",
                    label=title,
                    post_ids=[p.id for p in group_posts],
                    confidence_score=0.95,
                    key_themes=group_posts[0].tags if hasattr(group_posts[0], "tags") else ["Demo"],
                    representative_post_ids=[group_posts[0].id],
                    is_noise=False,
                )
            )
        return clusters
