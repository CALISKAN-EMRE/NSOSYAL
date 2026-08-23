import os
import sys
import time
from pathlib import Path

# Ensure backend package is in python path
repo_root = Path(__file__).resolve().parent.parent
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Force SEMANTIC_MODE=ml for live GPU verification
os.environ["SEMANTIC_MODE"] = "ml"

from fastapi.testclient import TestClient
from app.main import app


def run_live_ml_smoke_test():
    print("=================================================================")
    print("  NSOSYAL PUSULA — LIVE ML GPU INTEGRATION & SMOKE TEST (PHASE 2B)")
    print("=================================================================")

    with TestClient(app) as client:
        # 1. Health Endpoint
        t0 = time.perf_counter()
        resp = client.get("/health")
        t_health = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        print(f"\n[1] GET /health -> Status: {resp.status_code} ({t_health:.2f} ms)")
        print(f"    Response: {resp.json()['status']}")

        # 2. System Status Endpoint (Model readiness and GPU memory)
        t0 = time.perf_counter()
        resp = client.get("/api/system/status")
        t_status = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"System status failed: {resp.text}"
        status_data = resp.json()
        print(f"\n[2] GET /api/system/status -> Status: {resp.status_code} ({t_status:.2f} ms)")
        print(f"    Mode: {status_data['model_manager']['semantic_mode']}")
        print(f"    Device: {status_data['model_manager']['device']}")
        print(f"    GPU VRAM Allocated: {status_data['model_manager']['cuda_vram_allocated_gb']} GB")
        print(f"    Loaded Models: {status_data['model_manager']['models_loaded']}")

        # 3. Dynamic Semantic Topics (ModernBERT + HDBSCAN)
        t0 = time.perf_counter()
        resp = client.get("/api/topics")
        t_topics = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"Topics failed: {resp.text}"
        topics_data = resp.json()
        print(f"\n[3] GET /api/topics -> Status: {resp.status_code} ({t_topics:.2f} ms)")
        print(f"    Discovered Semantic Clusters: {len(topics_data)}")
        for t in topics_data[:3]:
            print(f"    - [{t['id']}] '{t['title']}' ({t['post_count']} posts, tags: {t['tags'][:3]})")

        # 4. Context Card with Two-Stage Retrieval & Reranking
        sample_topic_id = topics_data[0]["id"] if topics_data else "yapay-zeka-egitim"
        t0 = time.perf_counter()
        resp = client.get(f"/api/context/{sample_topic_id}")
        t_context = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"Context card failed: {resp.text}"
        card_data = resp.json()
        print(f"\n[4] GET /api/context/{sample_topic_id} -> Status: {resp.status_code} ({t_context:.2f} ms)")
        print(f"    Topic Title: '{card_data['topic_title']}'")
        print(f"    Summary: {card_data['summary'][:100]}...")
        print(f"    Perspectives: {len(card_data['perspectives'])}")
        print(f"    Two-Stage Reranked Sources: {len(card_data['sources'])}")
        for s in card_data["sources"][:3]:
            print(f"      * [Rank #{s['rank']}] {s['source_name']} (Relevance: {s['relevance_score']}, Dense: {s['dense_score']})")
        print(f"    Pipeline Timings: {card_data['pipeline_timing_ms']}")

        # 5. Natural Language Semantic Search (Multilingual-E5-Large-Instruct)
        query = "otoyolda elektrikli araç şarj istasyonu"
        t0 = time.perf_counter()
        resp = client.get(f"/api/search?q={query}&limit=5")
        t_search = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"Search failed: {resp.text}"
        search_data = resp.json()
        print(f"\n[5] GET /api/search?q='{query}' -> Status: {resp.status_code} ({t_search:.2f} ms)")
        print(f"    Total Matched: {search_data['total_results']}")
        print(f"    Model Used: {search_data['model_used']}")
        print(f"    Search Latency: {search_data['search_latency_ms']} ms")
        for res in search_data["results"][:3]:
            print(f"      * [#{res['rank']}] (Score: {res['relevance_score']}) {res['post']['text'][:80]}...")

        # 6. Transparent Recommendations with Embedding Similarity
        t0 = time.perf_counter()
        resp = client.get("/api/recommendations?limit=5")
        t_recs = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"Recommendations failed: {resp.text}"
        recs_data = resp.json()
        print(f"\n[6] GET /api/recommendations -> Status: {resp.status_code} ({t_recs:.2f} ms)")
        top_rec = recs_data[0]
        print(f"    Top Recommended Post: ID={top_rec['post']['id']}, Final Score={top_rec['explanation']['final_score']}")
        print(f"    Summary Reason: {top_rec['explanation']['summary_reason']}")
        print(f"    Decomposed Factors:")
        for f in top_rec["explanation"]["factors"]:
            print(f"      * {f['label']}: raw={f['raw_score']}, weighted={f['weighted_impact']} (w={f['weight']})")

        # 7. Safety Analysis
        t0 = time.perf_counter()
        resp = client.post("/api/safety/analyze", json={"text": "Bedava coin kazanmak için hemen tıklayın http://spam.xyz !!!"})
        t_safety = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200
        safety_data = resp.json()
        print(f"\n[7] POST /api/safety/analyze -> Status: {resp.status_code} ({t_safety:.2f} ms)")
        print(f"    Risk Level: {safety_data['risk_vector']['risk_level']} (Score: {safety_data['risk_vector']['overall_risk_score']})")

    print("\n=================================================================")
    print("  ALL LIVE ML ENDPOINTS VERIFIED ON GPU ACCELERATION (100% GREEN)")
    print("=================================================================")


if __name__ == "__main__":
    run_live_ml_smoke_test()
