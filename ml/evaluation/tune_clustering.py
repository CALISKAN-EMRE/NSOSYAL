import json
import sys
from pathlib import Path
import numpy as np
import re
from collections import Counter

repo_root = Path(__file__).resolve().parent.parent.parent
backend_dir = repo_root / "backend"
data_path = repo_root / "data" / "demo_posts.json"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA


def test_ctfidf_labeling():
    with open(data_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    texts = [p["text"] for p in posts]

    model = SentenceTransformer("ytu-ce-cosmos/modernbert-tr-embed", device="cuda")
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    # PCA 16d for HDBSCAN
    pca = PCA(n_components=min(16, len(texts) - 1), random_state=42)
    reduced = pca.fit_transform(embeddings)
    reduced = reduced / (np.linalg.norm(reduced, axis=1, keepdims=True) + 1e-12)

    clusterer = HDBSCAN(min_cluster_size=4, min_samples=2, metric="euclidean")
    labels = clusterer.fit_predict(reduced)

    print(f"Clustering Complete: {len(set(labels) - {-1})} clusters discovered.")

    # c-TF-IDF calculation
    stopwords = {
        "ve", "ile", "bir", "bu", "için", "de", "da", "çok", "daha", "en",
        "olan", "olarak", "gibi", "kadar", "sonra", "önce", "yeni", "tüm", "ne",
        "var", "yok", "her", "ama", "fakat", "çünkü", "nasıl", "neden", "şöyle",
        "tıklayın", "hemen", "kazanmak", "http", "https", "com", "xyz", "link",
        "ücretsiz", "bedava", "kazanç", "formu", "profilde", "göre", "bile", "artık",
        "ise", "ancak", "şekilde", "kendi", "hem", "özel", "eden", "oldu", "biri",
        "tarafından", "dair", "edildi", "ediliyor", "edilmelidir", "sağlandı", "sağlıyor"
    }

    clusters = {}
    for idx, lbl in enumerate(labels):
        clusters.setdefault(lbl, []).append(idx)

    # Clean tokens per cluster
    cluster_docs = {}
    all_cluster_terms = []
    for c_id, idxs in clusters.items():
        if c_id == -1:
            continue
        c_texts = [texts[i] for i in idxs]
        combined = " ".join(c_texts).lower()
        words = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{3,}\b", combined)
        filtered = [w for w in words if w not in stopwords and len(w) > 3]
        cluster_docs[c_id] = filtered
        all_cluster_terms.append(set(filtered))

    # c-TF-IDF scoring
    N_clusters = len(cluster_docs)
    for c_id, words in cluster_docs.items():
        tf = Counter(words)
        total_w = len(words)
        scores = {}
        for w, count in tf.items():
            df = sum(1 for terms in all_cluster_terms if w in terms)
            idf = np.log(1 + (N_clusters / (df + 1e-12)))
            scores[w] = (count / total_w) * idf

        top_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:4]
        distinctive = [t[0].capitalize() for t in top_terms]
        
        # Check exemplar post
        member_embs = embeddings[clusters[c_id]]
        cent = np.mean(member_embs, axis=0)
        sims = np.dot(member_embs, cent)
        best_post_idx = clusters[c_id][np.argmax(sims)]
        best_post_text = texts[best_post_idx]

        print(f"\nCluster {c_id} ({len(clusters[c_id])} posts):")
        print(f"  Distinctive terms: {', '.join(distinctive)}")
        print(f"  Exemplar post snippet: {best_post_text[:120]}...")


if __name__ == "__main__":
    test_ctfidf_labeling()
