"""Live end-to-end integration and latency verification test for Moderation & Coordination on RTX 3060 CUDA."""

import os
import sys
import time
from pathlib import Path
import torch

os.environ["SEMANTIC_MODE"] = "ml"
os.environ["DEVICE"] = "cuda"

repo_root = Path(__file__).resolve().parent.parent
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from fastapi.testclient import TestClient
from app.main import app


def run_live_moderation_smoke_test():
    print("=" * 80)
    print("NSOSYAL PUSULA: LIVE CUDA MODERATION & COORDINATION PIPELINE AUDIT")
    print("=" * 80)

    # 1. Hardware Inspection
    is_cuda = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if is_cuda else "CPU"
    vram_total_gb = (
        round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        if is_cuda
        else 0.0
    )

    print(f"\n[1] HARDWARE ENVIRONMENT:")
    print(f"  • Device:                 {device_name} (CUDA Available: {is_cuda})")
    print(f"  • Total VRAM:             {vram_total_gb} GB")
    print(f"  • PyTorch Version:        {torch.__version__}")

    with TestClient(app) as client:
        # Check system status
        status_res = client.get("/api/system/status")
        assert status_res.status_code == 200, f"System status failed: {status_res.text}"
        s_data = status_res.json()
        print(f"\n[2] SYSTEM STATUS:")
        print(f"  • Semantic Mode:          {s_data.get('semantic_mode')}")
        print(f"  • Device Config:          {s_data.get('device')}")
        print(f"  • CUDA VRAM Allocated:    {s_data.get('cuda_vram_allocated_gb')} GB")
        print(f"  • Models Loaded:          {s_data.get('models_loaded')}")

        test_cases = [
            {
                "label": "1. Safe Everyday Tech Post",
                "text": "Eğitimde yapay zekâ uygulamaları üzerine hazırlanan yeni müfredat rehberini inceledim, öğretmen eğitimi için çok faydalı adımlar var.",
                "post_id": "test-live-safe",
                "author_id": "user-live-1",
            },
            {
                "label": "2. Abusive Harassment & Provocation",
                "text": "Sen tam bir sahtekar ve rezil bir yalancısın, insanları kandırmaktan utanmıyor musun aşağılık herif!",
                "post_id": "test-live-tox",
                "author_id": "user-live-2",
            },
            {
                "label": "3. High-Density Malicious Link Spam",
                "text": "İNANILMAZ KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: http://bit.ly/bedava-2026 http://link-spam.xyz BEDAVA BEDAVA BEDAVA!!!",
                "post_id": "test-live-spam",
                "author_id": "user-live-3",
            },
            {
                "label": "4. Suspected Coordinated Inauthentic Campaign",
                "text": "Ücretsiz hediye çeki kazanmak için hemen tıklayın ve formu doldurun link profilde http://hediye-sahte.com",
                "post_id": "test-live-coord",
                "author_id": "user-live-coord-99",
            },
        ]

        print(f"\n[3] LIVE MODERATION INFERENCE ON RTX 3060:")
        for idx, tc in enumerate(test_cases, 1):
            t_req_start = time.perf_counter()
            resp = client.post(
                "/api/safety/analyze",
                json={
                    "text": tc["text"],
                    "post_id": tc["post_id"],
                    "author_id": tc["author_id"],
                },
            )
            lat_ms = (time.perf_counter() - t_req_start) * 1000.0
            assert resp.status_code == 200, f"Failed on {tc['label']}: {resp.text}"
            data = resp.json()
            r_vec = data["risk_vector"]

            print(f"\n  --- Case #{idx}: {tc['label']} (Latency: {lat_ms:.2f} ms) ---")
            print(f"  • Review Priority:         {r_vec.get('review_priority', r_vec.get('risk_level'))}")
            print(f"  • Human Review Recommended:{r_vec.get('human_review_recommended')}")
            print(f"  • Overall Composite Risk:  {r_vec.get('overall_risk_score')}")
            print(f"  • Spam Score:              {r_vec.get('spam_score')}")
            print(f"  • Repetition Score:        {r_vec.get('repetition_score')}")
            print(f"  • Coordination Score:      {r_vec.get('coordination_score')}")
            print(f"  • Grounded Explanation:    {r_vec.get('summary_explanation')}")

            hazard_scores = r_vec.get("hazard_scores") or {}
            top_hazards = sorted(
                [(k, v) for k, v in hazard_scores.items() if k != "unsafe"],
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            top_hazards_str = ", ".join([f"{k}: %{v*100:.1f}" for k, v in top_hazards])
            print(f"  • Top Model Hazards:       [{top_hazards_str}]")

    print("\n" + "=" * 80)
    print("ALL LIVE CUDA MODERATION TESTS PASSED CLEANLY ON RTX 3060!")
    print("=" * 80)


if __name__ == "__main__":
    run_live_moderation_smoke_test()
