from collections import Counter
import re
from typing import Any, Dict, List, Optional, Set
import numpy as np

from app.ml.base import BaseClusterService, BaseEmbeddingService, SemanticCluster


# Common Turkish stopwords and web artifacts for cleaning
TURKISH_STOPWORDS: Set[str] = {
    "ve", "ile", "bir", "bu", "için", "de", "da", "çok", "daha", "en",
    "olan", "olarak", "gibi", "kadar", "sonra", "önce", "yeni", "tüm", "ne",
    "var", "yok", "her", "ama", "fakat", "çünkü", "nasıl", "neden", "şöyle",
    "ise", "ancak", "şekilde", "kendi", "hem", "özel", "eden", "oldu", "biri",
    "tarafından", "dair", "edildi", "ediliyor", "edilmelidir", "sağlandı", "sağlıyor",
    "göre", "bile", "artık", "biz", "siz", "ben", "sen", "onlar", "bunu", "şunu",
    "http", "https", "com", "xyz", "link", "tıklayın", "hemen", "kazanmak",
    "ücretsiz", "bedava", "kazanç", "formu", "profilde", "sahte",
}

SPAM_KEYWORDS: Set[str] = {
    "airdrop", "usdt", "bitcoin", "kripto", "hediye", "kupon", "çeki",
    "dolandırıcılık", "sahte", "botnet", "bedava", "tıklayın", "garanti",
}


class SemanticClusterService(BaseClusterService):
    """Production unsupervised semantic clustering using ModernBERT-TR embeddings + PCA + HDBSCAN + c-TF-IDF."""

    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        min_cluster_size: int = 4,
        min_samples: Optional[int] = 2,
        pca_components: int = 16,
    ):
        self.embedding_service = embedding_service
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.pca_components = pca_components

    def cluster_posts(self, posts: List[Any]) -> List[SemanticCluster]:
        """Cluster posts into semantic groups strictly without reading any ground truth topic hints."""
        if not posts:
            return []

        if len(posts) < self.min_cluster_size:
            return [
                SemanticCluster(
                    cluster_id="semantic-cluster-1",
                    label=self._derive_topic_title([p.text for p in posts]),
                    post_ids=[p.id for p in posts],
                    confidence_score=1.0,
                    key_themes=self._extract_key_themes(posts),
                    representative_post_ids=[posts[0].id] if posts else [],
                    is_noise=False,
                )
            ]

        texts = [p.text for p in posts]
        embeddings = self.embedding_service.encode_documents(texts)

        # Normalize 768d embeddings to unit sphere
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        normed_embeddings = embeddings / norms

        # Dimensionality reduction (PCA) to overcome high-dimensional distance collapse in HDBSCAN
        n_samples = len(normed_embeddings)
        n_comp = min(self.pca_components, n_samples - 1)
        if n_comp >= 3 and n_samples >= 8:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=n_comp, random_state=42)
            reduced_vecs = pca.fit_transform(normed_embeddings)
            reduced_norms = np.linalg.norm(reduced_vecs, axis=1, keepdims=True)
            reduced_vecs = reduced_vecs / np.where(reduced_norms == 0, 1e-12, reduced_norms)
            cluster_input = reduced_vecs
        else:
            cluster_input = normed_embeddings

        # Run HDBSCAN
        labels, probabilities = self._run_hdbscan(cluster_input)

        # Group posts by cluster label
        clusters_dict: Dict[int, List[int]] = {}
        for idx, lbl in enumerate(labels):
            clusters_dict.setdefault(lbl, []).append(idx)

        # Compute centroids in original 768d space
        centroids: Dict[int, np.ndarray] = {}
        for lbl, member_indices in clusters_dict.items():
            if lbl != -1 and member_indices:
                cent = np.mean(normed_embeddings[member_indices], axis=0)
                cent = cent / (np.linalg.norm(cent) + 1e-12)
                centroids[lbl] = cent

        # Reassign noise points (-1) if cosine similarity >= 0.70 to any cluster centroid
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

                if best_lbl is not None and best_sim >= 0.70:
                    clusters_dict[best_lbl].append(n_idx)
                else:
                    unassigned_noise.append(n_idx)

            if unassigned_noise:
                clusters_dict[-1] = unassigned_noise
            else:
                del clusters_dict[-1]

        # Calculate c-TF-IDF across all discovered non-noise clusters
        non_noise_labels = [l for l in clusters_dict.keys() if l != -1]
        cluster_texts_map = {
            l: [texts[i] for i in clusters_dict[l]] for l in non_noise_labels
        }
        ctfidf_keywords = self._compute_ctfidf(cluster_texts_map)

        # Build SemanticCluster models
        result_clusters: List[SemanticCluster] = []
        cluster_counter = 1

        # Sort clusters by size descending
        sorted_labels = sorted(non_noise_labels, key=lambda l: len(clusters_dict[l]), reverse=True)

        for lbl in sorted_labels:
            indices = clusters_dict[lbl]
            cluster_posts = [posts[i] for i in indices]
            cluster_embs = normed_embeddings[indices]
            centroid = centroids.get(lbl, np.mean(cluster_embs, axis=0))

            # Exemplar posts closest to centroid
            sims = np.dot(cluster_embs, centroid)
            exemplar_sorted = [indices[i] for i in np.argsort(-sims)]
            representative_ids = [posts[i].id for i in exemplar_sorted[:3]]

            # Mathematical average membership probability from HDBSCAN
            cluster_probs = [probabilities[i] for i in indices if i < len(probabilities)]
            avg_prob = float(np.mean(cluster_probs)) if cluster_probs else 0.85

            # Distinctive terms from c-TF-IDF
            distinctive_terms = ctfidf_keywords.get(lbl, [])
            
            # Check if this cluster is promotional spam/botnet
            is_spam_cluster = self._is_spam_cluster(cluster_posts, distinctive_terms)

            if is_spam_cluster:
                cluster_label = "Tekrarlı Promosyon & Şüpheli Bağlantı Paylaşımları"
                is_noise_flag = False  # Dense semantic cluster containing spam, NOT HDBSCAN outlier
                cluster_id = f"semantic-spam-{cluster_counter}"
            else:
                cluster_label = self._format_topic_title(distinctive_terms, cluster_posts[0].text)
                is_noise_flag = False
                cluster_id = f"semantic-cluster-{cluster_counter}"

            key_themes = distinctive_terms[:5] if distinctive_terms else self._extract_key_themes(cluster_posts)

            result_clusters.append(
                SemanticCluster(
                    cluster_id=cluster_id,
                    label=cluster_label,
                    post_ids=[p.id for p in cluster_posts],
                    confidence_score=round(max(0.5, min(1.0, avg_prob)), 3),
                    key_themes=key_themes,
                    representative_post_ids=representative_ids,
                    is_noise=is_noise_flag,
                )
            )
            cluster_counter += 1

        # Add remaining noise/outlier cluster if present
        if -1 in clusters_dict and clusters_dict[-1]:
            noise_posts = [posts[i] for i in clusters_dict[-1]]
            result_clusters.append(
                SemanticCluster(
                    cluster_id="semantic-cluster-outliers",
                    label="Ayrık Günlük Paylaşımlar (Noise & Outliers)",
                    post_ids=[p.id for p in noise_posts],
                    confidence_score=0.35,
                    key_themes=["Ayrık", "Genel", "Gündem"],
                    representative_post_ids=[p.id for p in noise_posts[:2]],
                    is_noise=True,
                )
            )

        return result_clusters

    def _run_hdbscan(self, embeddings: np.ndarray) -> tuple:
        """Run HDBSCAN on input vectors."""
        try:
            from sklearn.cluster import HDBSCAN
            clusterer = HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(embeddings)
            probabilities = getattr(
                clusterer, "probabilities_", np.ones(len(embeddings), dtype=float)
            )
            return labels, probabilities
        except Exception:
            n_samples = len(embeddings)
            labels = np.zeros(n_samples, dtype=int)
            return labels, np.ones(n_samples, dtype=float) * 0.85

    def _compute_ctfidf(self, cluster_texts_map: Dict[int, List[str]]) -> Dict[int, List[str]]:
        """Compute Class-based TF-IDF (c-TF-IDF) to find distinctive terms per cluster."""
        cluster_docs: Dict[int, List[str]] = {}
        all_cluster_terms: List[Set[str]] = []

        for c_id, texts in cluster_texts_map.items():
            combined = " ".join(texts).lower()
            words = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{3,}\b", combined)
            filtered = [w for w in words if w not in TURKISH_STOPWORDS and len(w) > 3]
            cluster_docs[c_id] = filtered
            all_cluster_terms.append(set(filtered))

        N_clusters = len(cluster_docs)
        results: Dict[int, List[str]] = {}

        for c_id, words in cluster_docs.items():
            if not words:
                results[c_id] = ["Gündem"]
                continue

            tf = Counter(words)
            total_w = len(words)
            scores: Dict[str, float] = {}

            for w, count in tf.items():
                df = sum(1 for terms in all_cluster_terms if w in terms)
                idf = np.log(1.0 + (N_clusters / (df + 1e-12)))
                scores[w] = (count / total_w) * idf

            top_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
            results[c_id] = [t[0].capitalize() for t in top_terms]

        return results

    def _format_topic_title(self, distinctive_terms: List[str], sample_text: str) -> str:
        """Format a natural, human-readable Turkish topic title dynamically from c-TF-IDF terms.

        Strictly unsupervised and deterministic; zero hard-coded topic mappings or ground-truth leakage.
        """
        if not distinctive_terms:
            return "Genel Tartışma ve Gündem"

        clean_terms = [t.strip().capitalize() for t in distinctive_terms if len(t.strip()) > 2]
        if not clean_terms:
            return "Genel Tartışma ve Gündem"

        if len(clean_terms) >= 3:
            return f"{clean_terms[0]}, {clean_terms[1]} ve {clean_terms[2]}"
        elif len(clean_terms) == 2:
            return f"{clean_terms[0]} ve {clean_terms[1]}"
        else:
            return f"{clean_terms[0]} Odaklı Paylaşımlar"

    def _is_spam_cluster(self, posts: List[Any], distinctive_terms: List[str]) -> bool:
        """Identify if cluster consists predominantly of spam or bot repetition."""
        terms_lower = [t.lower() for t in distinctive_terms]
        spam_hits = sum(1 for t in terms_lower if t in SPAM_KEYWORDS)
        if spam_hits >= 2:
            return True

        # Check post text patterns
        bot_hits = 0
        for p in posts:
            lower_text = p.text.lower()
            if any(k in lower_text for k in ["usdt", "airdrop", "hediye çeki", "http://", "bedava"]):
                bot_hits += 1

        return (bot_hits / len(posts)) >= 0.50

    def _derive_topic_title(self, texts: List[str]) -> str:
        words = []
        for t in texts:
            clean = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", t.lower())
            words.extend([w for w in clean if w not in TURKISH_STOPWORDS])
        top_words = [w.capitalize() for w, _ in Counter(words).most_common(2)]
        return " & ".join(top_words) if top_words else "Semantik Tartışma Grubu"

    def _extract_key_themes(self, posts: List[Any]) -> List[str]:
        words = []
        for p in posts:
            clean = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", p.text.lower())
            words.extend([w for w in clean if w not in TURKISH_STOPWORDS])
        counts = Counter(words)
        return [w.capitalize() for w, _ in counts.most_common(5)] or ["Genel Tartışma"]


class DemoClusterService(BaseClusterService):
    """Deterministic cluster service for demo mode / testing."""

    def cluster_posts(self, posts: List[Any]) -> List[SemanticCluster]:
        if not posts:
            return []

        groups: Dict[str, List[Any]] = {}
        for p in posts:
            t_id = getattr(p, "topic_id", "genel")
            groups.setdefault(t_id, []).append(p)

        clusters = []
        for idx, (t_id, group_posts) in enumerate(groups.items(), 1):
            title = getattr(group_posts[0], "topic_title", t_id.replace("-", " ").title())
            is_noise = (t_id == "spam-noise")
            clusters.append(
                SemanticCluster(
                    cluster_id=f"demo-cluster-{idx}",
                    label=title,
                    post_ids=[p.id for p in group_posts],
                    confidence_score=0.95 if not is_noise else 0.40,
                    key_themes=group_posts[0].tags if hasattr(group_posts[0], "tags") else ["Demo"],
                    representative_post_ids=[group_posts[0].id],
                    is_noise=is_noise,
                )
            )
        return clusters
