# NSosyal Pusula 🧭
### Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi
**TEKNOFEST 2026 NSosyal İnovasyon Yarışması — Çalışan Yarışma Prototipi**

[![Prototip Durumu](https://img.shields.io/badge/Prototip-Çalışan_Üretim_Mimarisi-emerald.svg)](docs/report_assets/technical_evidence_summary.md)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-green.svg)](LICENSE)
[![GPU Desteği](https://img.shields.io/badge/Hızlandırma-NVIDIA_CUDA_RTX_3060-blue.svg)](#donanım-ve-çalışma-ortamı)
[![Veri Kaynağı](https://img.shields.io/badge/Veri_Kaynağı-Sentetik_Türkçe_Demo-orange.svg)](#veri-ve-entegrasyon-uyarısı)

---

## 📌 Proje Genel Bakışı (Project Overview)

**NSosyal Pusula**, modern sosyal medya platformlarında bilgi kirliliği, kutuplaşma, şeffaf olmayan algoritmalar ve bağlamından koparılmış içerik akışlarına karşı geliştirilmiş **yapay zekâ destekli bir sosyal medya zekâ, şeffaflık ve moderasyon katmanıdır**.

Platform, kullanıcılara salt kronolojik veya gizli öneri motorlarına dayalı bir akış sunmak yerine; paylaşımları anlamsal olarak kümeleyen, çoklu bakış açılarını sentezleyen **Bağlam Kartları (Context Cards)**, önerilerin gerekçelerini matematiksel ve metinsel olarak açıklayan **Şeffaf Öneri Sistemi (Transparent Recommendations)**, talimat güdümlü **Doğal Dil Arama (Natural Language Semantic Search)** ve 11 tehlike sınıfında kalibre edilmiş **İçerik Güvenlik & Moderasyon Katmanı (Calibrated Safety & Coordination Defense)** sağlar.

---

## 🚀 Üretim Yapay Zekâ ve Semantik ML Yetenekleri

Sistem, bağımsız bilimsel testlerle doğrulanmış Türkçe NLP modelleri ile donatılmıştır:

| Boru Hattı (Pipeline) | Seçilen Model & Mimarisi | Fonksiyon ve Görevi |
| :--- | :--- | :--- |
| **1. Olay & Konu Kümeleme** | **`ytu-ce-cosmos/modernbert-tr-embed`** + HDBSCAN | Metinleri 768d vektörlerle temsil eder, PCA (16d) ve HDBSCAN ile dinamik konuları keşfeder. |
| **2. İki Aşamalı Bağlam Erişimi (Stage 1)** | **`ytu-ce-cosmos/modernbert-tr-embed`** (Dense) | Konu özetiyle ilişkili aday kaynak dokümanlardan ilk 15 adayı (Top-15) çeker. |
| **3. İki Aşamalı Yeniden Sıralama (Stage 2)** | **`ytu-ce-cosmos/modernbert-tr-reranker`** (Cross-Encoder) | Top-15 adayı çapraz dikkat ile puanlar, yüksek relevanslı kaynakları sıralar (+0.0115 nDCG artışı). |
| **4. Doğal Dil Arama** | **`intfloat/multilingual-e5-large-instruct`** | Türkçe arama sorgularını talimat formatında (`Instruct: ...`) kodlayarak anlam eşleşmesi sağlar. |
| **5. İçerik Güvenliği ve Moderasyon** | **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 11 tehlike sınıfında çok etiketli risk sınıflandırması ve kalibre edilmiş karar eşikleri (%93.77 Unsafe F1). |
| **6. Çok Katmanlı Risk Füzyonu** | **`ModerationFusionService`** | Guardrail + Sezgisel Spam + Metin İçi/Külliyat Tekrarı + Çoklu Hesap Koordineli Botnet Tespiti. |

---

## 🎯 Şeffaf Öneri Formülü (Explainable Recommendation Engine)

Her önerilen içerik için "Neden bunu görüyorum?" paneli açılabilir ve aşağıdaki matematiksel ayrışım kullanıcıya sunulur:

$$\text{Toplam Skor} = (w_1 \cdot \text{Anlamsal İlgi}) + (w_2 \cdot \text{Konu Yakınlığı}) + (w_3 \cdot \text{Güncellik}) + (w_4 \cdot \text{Çeşitlilik}) - (w_5 \cdot \text{Tekrar Cezası}) - (w_6 \cdot \text{Güvenlik Riski})$$

* $w_1 = 30$ (ModernBERT Vektör Kosinüs Benzerliği)
* $w_2 = 25$ (Kullanıcının tercih ettiği konu kategorisiyle etkileşimi)
* $w_3 = 20$ (Zaman aşımı üstel sönümleme fonksiyonu)
* $w_4 = 15$ (Yankı odasını kırmak için uzman/akademik/eleştirel bakış açısı ödülü)
* $w_5 = -20$ (Aynı metin veya bot tekrarı cezası)
* $w_6 = -30$ (Çoklu sinyal moderasyon risk cezası)

---

## 🏗️ Proje Dizin Yapısı (Project Structure)

```
NSOSYAL/
├── backend/                   # Python / FastAPI REST Servisi
│   ├── app/
│   │   ├── adapters/          # DataSourceAdapter (JsonDemoAdapter & Gelecek API adaptörleri)
│   │   ├── api/               # REST API yönlendirmeleri (/health, /api/posts, /api/search, /api/system, vb.)
│   │   ├── ml/                # Faz 2B Üretim ML Modülü (ModelManager, Embedding, Cluster, Reranker)
│   │   ├── models/            # Pydantic veri modelleri ve şemalar
│   │   ├── services/          # ContextService, RecommendationService, SearchService, SafetyService
│   │   └── config.py          # Konfigürasyon ve SEMANTIC_MODE ayarları
│   └── requirements.txt
├── frontend/                  # Next.js 14 / TypeScript / Tailwind CSS Kullanıcı Arayüzü
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   ├── components/        # Feed, SemanticSearchBar, ContextCardModal, ExplainModal, SafetyPanel
│   │   └── lib/               # API istemcisi ve TypeScript tip tanımları
│   └── package.json
├── data/                      # Sentetik Türkçe Sosyal Medya Veri Seti
│   └── demo_posts.json
├── docs/                      # Detaylı Mimari ve Süreç Dokümantasyonu
│   ├── architecture.md        # Sistem genel mimarisi
│   └── semantic_pipeline.md   # Model seçim gerekçeleri, benchmark kanıtları ve boru hatları
├── ml/                        # Faz 2A Araştırma ve Karşılaştırma Laboratuvarı
│   ├── evaluation/            # STS, Kümeleme, Erişim ve Reranker test scriptleri
│   └── reports/               # embedding_model_selection.md, benchmark_integrity_audit.md
└── tests/                     # Backend Pytest birim, entegrasyon ve canlı GPU smoke testleri
```

---

## 🛠️ Yerel Geliştirme Kurulumu (Local Development Setup)

### Sistem Gereksinimleri
* **Python:** 3.10+ (Test edilen: Python 3.13.7)
* **Node.js:** 18+ (Test edilen: Node.js 20+)
* **GPU (Opsiyonel ama Tavsiye Edilen):** NVIDIA GPU with CUDA (Test edilen: NVIDIA RTX 3060 12GB VRAM)

### 1. Depoyu Klonlayın ve Yapılandırın
```bash
git clone <repository-url>
cd NSOSYAL
cp .env.example .env
```

### 2. Backend Kurulumu ve Çalıştırma (ML Modu)
```bash
cd backend
python -m venv .venv

# Windows Powershell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
> **Not:** Sistem varsayılan olarak `SEMANTIC_MODE=ml` modunda açılır ve modelleri GPU üzerine yükler. Model indirmeden hızlı çalıştırmak için `.env` dosyasına `SEMANTIC_MODE=demo` yazabilirsiniz.

* **API Dökümantasyonu (Swagger):** `http://localhost:8000/docs`
* **Sistem & Model Durumu:** `http://localhost:8000/api/system/status`

### 3. Frontend Kurulumu ve Çalıştırma
Yeni bir terminalde:
```bash
cd frontend
npm install
npm run dev
```
* **Web Arayüzü:** `http://localhost:3000`

### 4. Testleri Çalıştırma
```bash
# Hızlı Birim Testleri (Demo Modu - 1.5 saniye):
python -m pytest tests -v

# Canlı GPU ML Entegrasyon Testi:
python -m tests.smoke_test_ml_live
```

---

## ⚠️ Veri ve Entegrasyon Uyarısı (Important Disclosures)

1. **API Erişimi:** Bu proje bir TEKNOFEST 2026 yarışma prototipidir. Mevcut aşamada sistem **herhangi bir canlı/resmi NSosyal API'sine bağlı değildir** ve yetkisiz veri kazıma (scraping) yapılmamaktadır.
2. **Sentetik Veri:** Sistemde kullanılan paylaşımlar (`data/demo_posts.json`), prototipin yeteneklerini test etmek üzere kurgulanmış **sentetik Türkçe içeriklerdir**.
3. **Model Hakları ve Atıf:** Kullanılan modeller (`ytu-ce-cosmos/modernbert-tr-embed`, `ytu-ce-cosmos/modernbert-tr-reranker`, `intfloat/multilingual-e5-large-instruct`) ilgili yazarların açık kaynak lisanslarına (Apache-2.0 / MIT) tabidir.
