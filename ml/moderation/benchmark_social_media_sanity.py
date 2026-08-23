"""Project-specific Social Media Moderation & Coordination Sanity Evaluation.

Evaluates ModerationFusionService against representative synthetic social media scenarios:
1. Benign/safe everyday discussions
2. Toxicity & harassment
3. Hate/discriminatory risk language
4. Spam & deceptive link campaigns
5. Near-duplicate promotional bursts
6. Suspected coordinated inauthentic behavior across multiple accounts

NOTE ON METHODOLOGY:
This dataset is a curated SYNTHETIC evaluation suite designed specifically to audit
multi-dimensional moderation fusion, candidate gating, and false-positive resilience
in Turkish social media contexts. It is NOT human-annotated organic platform data.
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from backend.app.moderation.base import (
    ModerationAnalysisRequest,
    ReviewPriority,
)
from backend.app.moderation.fusion_service import ModerationFusionService
from backend.app.moderation.guardrail_classifier import ModernBERTGuardrailClassifier, DemoGuardrailClassifier


SYNTHETIC_SANITY_DATASET: List[Dict[str, Any]] = [
    # --- Category 1: Safe Benign Posts ---
    {
        "id": "sanity-001",
        "text": "Eğitimde yapay zekâ uygulamaları üzerine hazırlanan yeni müfredat rehberini inceledim, öğretmen eğitimi için çok faydalı adımlar var.",
        "author_id": "user-s1",
        "expected_priority": "LOW",
        "expected_review": False,
        "hazard_type": "SAFE",
    },
    {
        "id": "sanity-002",
        "text": "Şehirlerarası otoyollarda elektrikli araç şarj istasyonlarının artması seyahat planlamasını oldukça kolaylaştırdı.",
        "author_id": "user-s2",
        "expected_priority": "LOW",
        "expected_review": False,
        "hazard_type": "SAFE",
    },
    {
        "id": "sanity-003",
        "text": "Kamuda Pardus ve açık kaynak yazılım kullanımı sayesinde hem lisans maliyetleri düşüyor hem de dijital egemenlik güçleniyor.",
        "author_id": "user-s3",
        "expected_priority": "LOW",
        "expected_review": False,
        "hazard_type": "SAFE",
    },
    {
        "id": "sanity-004",
        "text": "TÜRKSAT 6A yerli haberleşme uydumuzun yörünge testleri başarıyla devam ediyor, mühendislerimizi tebrik ederim.",
        "author_id": "user-s4",
        "expected_priority": "LOW",
        "expected_review": False,
        "hazard_type": "SAFE",
    },
    # --- Category 2: Harassment / Insult ---
    {
        "id": "sanity-005",
        "text": "Sen tam bir sahtekar ve rezil bir yalancısın, insanları kandırmaktan utanmıyor musun aşağılık herif!",
        "author_id": "user-s5",
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "HARASSMENT_OFFENSIVE",
    },
    {
        "id": "sanity-006",
        "text": "Aptal aptal konuşma, yazdığın hiçbir şeyin mantığı yok, pislik herif defol git buradan.",
        "author_id": "user-s6",
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "HARASSMENT_OFFENSIVE",
    },
    # --- Category 3: Hate & Discrimination ---
    {
        "id": "sanity-007",
        "text": "Belli bir etnik kökene sahip insanlardan nefret ediyorum, bu ülkedeki tüm bu ırk mensupları zorla sürülmeli.",
        "author_id": "user-s7",
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "HATE_DISCRIMINATION",
    },
    # --- Category 4: Spam & Malicious Links ---
    {
        "id": "sanity-008",
        "text": "İNANILMAZ KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: http://bit.ly/bedava-2026 http://link-spam.xyz BEDAVA BEDAVA BEDAVA!!!",
        "author_id": "user-s8",
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "SPAM",
    },
    {
        "id": "sanity-009",
        "text": "Bedava 500 USDT airdrop anında hesabında! Kaçırma hemen tıkla ve formu doldur: http://promo-fake.site",
        "author_id": "user-s9",
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "SPAM",
    },
    # --- Category 5: Coordinated Duplicate Campaign ---
    {
        "id": "sanity-010",
        "text": "Ücretsiz hediye çeki kazanmak için hemen tıklayın ve formu doldurun link profilde http://hediye-sahte.com",
        "author_id": "bot-acc-1",
        "created_at": datetime(2026, 8, 23, 14, 0, 0),
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "COORDINATED_SPAM",
    },
    {
        "id": "sanity-011",
        "text": "Ücretsiz hediye çeki kazanmak için hemen tıklayın ve formu doldurun link profilde http://hediye-sahte.com",
        "author_id": "bot-acc-2",
        "created_at": datetime(2026, 8, 23, 14, 5, 0),
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "COORDINATED_SPAM",
    },
    {
        "id": "sanity-012",
        "text": "Ücretsiz hediye çeki kazanmak için hemen tıklayın ve formu doldurun link profilde http://hediye-sahte.com",
        "author_id": "bot-acc-3",
        "created_at": datetime(2026, 8, 23, 14, 10, 0),
        "expected_priority": "HIGH",
        "expected_review": True,
        "hazard_type": "COORDINATED_SPAM",
    },
]


def run_sanity_evaluation(use_ml_model: bool = True):
    print("=" * 70)
    print("RUNNING SYNTHETIC SOCIAL MEDIA MODERATION SANITY BENCHMARK")
    print("=" * 70)

    classifier = ModernBERTGuardrailClassifier() if use_ml_model else DemoGuardrailClassifier()
    fusion_service = ModerationFusionService(classifier=classifier)

    results = []
    correct_review_flags = 0
    total_samples = len(SYNTHETIC_SANITY_DATASET)

    # Convert dataset to post objects for cross-post matching
    existing_posts = [
        {
            "id": s["id"],
            "text": s["text"],
            "author": {"id": s["author_id"], "name": s["author_id"], "handle": f"@{s['author_id']}"},
            "created_at": s.get("created_at", datetime(2026, 8, 23, 12, 0, 0)),
        }
        for s in SYNTHETIC_SANITY_DATASET
    ]

    for item in SYNTHETIC_SANITY_DATASET:
        req = ModerationAnalysisRequest(
            text=item["text"],
            post_id=item["id"],
            author_id=item["author_id"],
            created_at=item.get("created_at"),
        )
        resp = fusion_service.analyze(req, existing_posts=existing_posts)
        r_vec = resp.risk_vector

        is_review_match = (r_vec.human_review_recommended == item["expected_review"])
        if is_review_match:
            correct_review_flags += 1

        results.append({
            "id": item["id"],
            "hazard_type": item["hazard_type"],
            "expected_review": item["expected_review"],
            "predicted_review": r_vec.human_review_recommended,
            "review_priority": r_vec.review_priority.value,
            "overall_unsafe": r_vec.overall_unsafe_probability,
            "spam_score": r_vec.spam_score,
            "repetition_score": r_vec.repetition_score,
            "coordination_score": r_vec.suspected_coordination_score,
            "explanation": r_vec.summary_explanation,
        })

        print(f"\n[{item['id']}] Category: {item['hazard_type']:20s} | Review Expected: {str(item['expected_review']):5s} -> Predicted: {str(r_vec.human_review_recommended):5s} ({r_vec.review_priority.value})")
        print(f"  Text: '{item['text'][:70]}...'")
        print(f"  Scores: Unsafe={r_vec.overall_unsafe_probability:.2f}, Spam={r_vec.spam_score:.2f}, Repetition={r_vec.repetition_score:.2f}, Coord={r_vec.suspected_coordination_score:.2f}")
        print(f"  Explanation: {r_vec.summary_explanation}")

    passed_count = correct_review_flags
    print("\n" + "=" * 70)
    print(f"CONTROLLED SANITY SCENARIOS PASSED: {passed_count}/{total_samples} ({(passed_count/total_samples)*100:.1f}%)")
    print("=" * 70)

    out_file = "ml/evaluation/results/sanity_moderation_evaluation.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_controlled_scenarios": total_samples,
            "scenarios_passed": passed_count,
            "pass_rate_percent": round((passed_count / total_samples) * 100.0, 2),
            "results": results
        }, f, ensure_ascii=False, indent=2)

    return passed_count


if __name__ == "__main__":
    run_sanity_evaluation(use_ml_model=True)
