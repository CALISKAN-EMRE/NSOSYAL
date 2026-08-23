import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from sklearn.feature_extraction.text import TfidfVectorizer


class BaseClusterer:
    """Base interface for clustering algorithms."""

    def fit_predict(self, embeddings: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class DeterministicKMeansClusterer(BaseClusterer):
    """Spherical / Cosine K-Means clustering with fixed random seed for reproducibility."""

    def __init__(self, n_clusters: int = 5, random_state: int = 42, max_iter: int = 100):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.max_iter = max_iter

    def fit_predict(self, embeddings: np.ndarray) -> np.ndarray:
        n_samples = embeddings.shape[0]
        if n_samples <= self.n_clusters:
            return np.arange(n_samples)

        # Normalize embeddings to unit hypersphere
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        normed = embeddings / norms

        # Deterministic centroid initialization (k-means++ style seeded)
        np.random.seed(self.random_state)
        centroids = [normed[np.random.choice(n_samples)]]

        for _ in range(1, self.n_clusters):
            # Compute distance to nearest centroid
            dists = np.array([1.0 - np.max(np.dot(normed, np.array(centroids).T), axis=1)])
            dists = np.maximum(0, dists)
            probs = dists / (np.sum(dists) + 1e-12)
            next_idx = np.random.choice(n_samples, p=probs.flatten())
            centroids.append(normed[next_idx])

        centroids = np.array(centroids)
        labels = np.zeros(n_samples, dtype=int)

        for _ in range(self.max_iter):
            # Assign points to nearest centroid (max cosine similarity)
            similarities = np.dot(normed, centroids.T)
            new_labels = np.argmax(similarities, axis=1)

            if np.array_equal(labels, new_labels):
                break
            labels = new_labels

            # Recompute centroids
            for k in range(self.n_clusters):
                mask = labels == k
                if np.any(mask):
                    new_cent = np.mean(normed[mask], axis=0)
                    cent_norm = np.linalg.norm(new_cent)
                    centroids[k] = new_cent / (cent_norm + 1e-12)

        return labels


class HDBSCANClusterer(BaseClusterer):
    """HDBSCAN density-based clustering for discovering natural clusters without prespecifying K."""

    def __init__(
        self,
        min_cluster_size: int = 3,
        min_samples: Optional[int] = 2,
        metric: str = "euclidean",
    ):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric

    def fit_predict(self, embeddings: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        normed = embeddings / norms

        try:
            from sklearn.cluster import HDBSCAN

            clusterer = HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric=self.metric,
            )
            return clusterer.fit_predict(normed)
        except (ImportError, AttributeError):
            try:
                import hdbscan

                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=self.min_cluster_size,
                    min_samples=self.min_samples,
                    metric=self.metric,
                )
                return clusterer.fit_predict(normed)
            except ImportError:
                return self._density_fallback(normed)

    def _density_fallback(self, normed: np.ndarray) -> np.ndarray:
        n_samples = normed.shape[0]
        labels = -np.ones(n_samples, dtype=int)
        visited = set()
        cluster_id = 0
        similarity_threshold = 0.75

        sim_matrix = np.dot(normed, normed.T)

        for i in range(n_samples):
            if i in visited:
                continue
            visited.add(i)
            neighbors = [j for j in range(n_samples) if sim_matrix[i, j] >= similarity_threshold]

            if len(neighbors) >= self.min_cluster_size:
                labels[i] = cluster_id
                queue = list(neighbors)
                while queue:
                    curr = queue.pop(0)
                    if curr not in visited:
                        visited.add(curr)
                        curr_neighbors = [
                            k
                            for k in range(n_samples)
                            if sim_matrix[curr, k] >= similarity_threshold
                        ]
                        if len(curr_neighbors) >= self.min_cluster_size:
                            queue.extend(curr_neighbors)
                    if labels[curr] == -1:
                        labels[curr] = cluster_id
                cluster_id += 1

        return labels


class TfIdfSphericalKMeansClusterer:
    """Label-blind unsupervised baseline: TF-IDF Bag-of-Words + Spherical K-Means."""

    def __init__(self, n_clusters: int = 6, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))

    def fit_predict_texts(self, texts: List[str]) -> np.ndarray:
        tfidf_matrix = self.vectorizer.fit_transform(texts).toarray()
        kmeans = DeterministicKMeansClusterer(
            n_clusters=self.n_clusters, random_state=self.random_state
        )
        return kmeans.fit_predict(tfidf_matrix)


class RandomClusterer:
    """Random assignment baseline for clustering lower-bound calibration."""

    def __init__(self, n_clusters: int = 6, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def fit_predict(self, n_samples: int) -> np.ndarray:
        np.random.seed(self.random_state)
        return np.random.randint(0, self.n_clusters, size=n_samples)


class OracleMetadataGroupingBaseline:
    """SUPERVISED ORACLE BASELINE: Grouping using hand-crafted regex keyword sets.

    NOTE: This is NOT a fair unsupervised clustering model; it directly leverages curated
    ground-truth keywords as an oracle reference upper bound.
    """

    def __init__(self):
        self.known_topics = {
            "yapay_zeka_egitim": ["milli eğitim", "liselerde", "öğrenci", "okul", "ders", "müfredat"],
            "yapay_zeka_etik_hukuk": ["telif", "hukuk", "deepfake", "biyometrik", "patent", "yasal"],
            "sarj_altyapisi_otoyol": ["ankara-istanbul", "otoban", "otoyol", "dinlenme tesisi", "epdk", "ultra hızlı dc"],
            "sarj_altyapisi_sehirici": ["apartman", "site", "kapalı otopark", "ev tipi", "22kw", "monofaze"],
            "uzay_ve_uydu": ["türksat", "imece", "uydu", "fırlatıldı", "yörünge", "uzay ajansı"],
            "acik_kaynak_kamu": ["pardus", "postgresql", "açık kaynak", "linux", "bakanlık", "tasarruf"],
        }

    def predict_texts(self, texts: List[str]) -> np.ndarray:
        labels = []
        for text in texts:
            t_lower = text.lower()
            best_topic = -1
            max_matches = 0
            for idx, (t_name, keywords) in enumerate(self.known_topics.items()):
                matches = sum(1 for kw in keywords if kw in t_lower)
                if matches > max_matches:
                    max_matches = matches
                    best_topic = idx
            labels.append(best_topic)
        return np.array(labels, dtype=int)
