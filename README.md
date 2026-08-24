# NSosyal Pusula 🧭
### Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi
**TEKNOFEST 2026 NSosyal İnovasyon Yarışması — Çalışan Yarışma Prototipi**

[![CI](https://github.com/CALISKAN-EMRE/NSOSYAL/actions/workflows/ci.yml/badge.svg)](https://github.com/CALISKAN-EMRE/NSOSYAL/actions/workflows/ci.yml)
[![Prototip Durumu](https://img.shields.io/badge/Prototip-Çalışan_Üretim_Mimarisi-emerald.svg)](docs/report_assets/technical_evidence_summary.md)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-green.svg)](LICENSE)
[![GPU Desteği](https://img.shields.io/badge/Hızlandırma-NVIDIA_CUDA_RTX_3060-blue.svg)](#-donanım-ve-çalışma-ortamı-donanım-referansı)
[![Veri Kaynağı](https://img.shields.io/badge/Veri_Kaynağı-Sentetik_Türkçe_Demo-orange.svg)](#-veri-ve-entegrasyon-uyarısı-important-disclosures)

> **📌 TEKNOFEST 2026 TTR Submission Snapshot:**  
> `teknofest-2026-ttr-submission` etiketi (Git tag), jüriye sunulan Teknik Tasarım Raporu (TTR) ile ilişkili kaynak kod durumunu muhafaza eder. Bu etiket sonrasındaki commit'ler yalnızca mühendislik sağlamlaştırması, CI/CD iş akışları, bağımlılık ayrıştırması ve tekrarlanabilirlik iyileştirmelerini içermektedir.

---

## 📌 Proje Genel Bakışı (Project Overview)

**NSosyal Pusula**, modern sosyal medya platformlarında bilgi kirliliği, kutuplaşma, şeffaf olmayan algoritmalar ve bağlamından koparılmış içerik akışlarına karşı geliştirilmiş **yapay zekâ destekli bir sosyal medya zekâ, şeffaflık ve moderasyon katmanıdır**.

Platform, kullanıcılara salt kronolojik veya kapalı kutu öneri motorlarına dayalı bir akış sunmak yerine; paylaşımları anlamsal olarak kümeleyen, çoklu bakış açılarını sentezleyen **Bağlam Kartları (Context Cards)**, önerilerin gerekçelerini matematiksel ve metinsel olarak açıklayan **Şeffaf Öneri Sistemi (Transparent Recommendations)**, talimat güdümlü **Doğal Dil Arama (Natural Language Semantic Search)** ve 11 tehlike sınıfında kalibre edilmiş **İçerik Güvenlik & Moderasyon Katmanı (Calibrated Safety & Coordination Defense)** sağlar.

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

## 💻 Donanım ve Çalışma Ortamı (Donanım Referansı)

Raporlanan tüm bilimsel ölçümler, model gecikmeleri ve prototip ekran görüntüleri aşağıdaki donanım ortamında kaydedilmiştir:

| Donanım / Yazılım Bileşeni | Referans Spesifikasyon |
| :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 3060 (Masaüstü, 12.0 GB GDDR6 VRAM) |
| **CPU** | 13th Gen Intel(R) Core(TM) i5-13600KF (14 Çekirdek, 20 İş Parçacığı) |
| **RAM** | 32.0 GB (31.82 GB kullanılabilir) |
| **CUDA & PyTorch** | CUDA 12.4 / PyTorch 2.6.0+cu124 |
| **Python & Node.js** | Python 3.13.7 (3.11+ desteklenir) / Node.js 20+ |

---

## 🏗️ Proje Dizin Yapısı (Project Structure)

```
NSOSYAL/
├── .github/workflows/         # GitHub Actions CI iş akışı (ci.yml)
├── backend/                   # Python / FastAPI REST Servisi (v0.2.0)
│   ├── app/
│   │   ├── adapters/          # JsonDemoAdapter (70 sentetik gönderi)
│   │   ├── api/               # REST API yönlendirmeleri (/health, /api/posts, /api/search, /api/system)
│   │   ├── ml/                # Üretim ML Modülleri (ModernBERT, E5, Reranker, HDBSCAN)
│   │   ├── moderation/        # Guardrail Sınıflandırıcısı, Spam, Tekrar & Koordinasyon Tespiti
│   │   ├── models/            # Pydantic veri modelleri ve şemalar
│   │   ├── services/          # ContextService, RecommendationService, SearchService, SafetyService
│   │   └── config.py          # Sistem konfigürasyonu ve SEMANTIC_MODE ayarları
│   ├── requirements.txt       # Çekirdek / Demo modu bağımlılıkları (Hafif, model indirmesiz)
│   ├── requirements-ml.txt    # Tam ML üretim bağımlılıkları (PyTorch, Transformers, Scikit-learn)
│   └── pyproject.toml         # Paket metadata ve dev/ml opsiyonel bağımlılıkları
├── frontend/                  # Next.js 14 / TypeScript / Tailwind CSS Kullanıcı Arayüzü
│   ├── src/
│   │   ├── app/               # Next.js App Router (page.tsx, globals.css)
│   │   ├── components/        # Feed, SemanticSearchBar, ContextCardModal, ExplainModal, SafetyPanel
│   │   └── lib/               # API istemcisi ve TypeScript tip tanımları
│   └── package.json
├── data/                      # Sentetik Türkçe Sosyal Medya Veri Seti (demo_posts.json)
├── docs/                      # Mimari ve Teknik Rapor Kanıt Varlıkları
│   └── report_assets/         # Grafikler, diyagramlar, sayısal tablolar ve prototip ekran görüntüleri
├── ml/                        # Araştırma, Karşılaştırma ve Raporlama Betikleri
│   ├── evaluation/            # Model karşılaştırma ve kalibrasyon betikleri
│   └── reports/               # Rapor kanıt paketi üreticisi (generate_report_evidence_pack.py)
├── scripts/                   # Tek komutla çalıştırma betikleri (run_demo, run_ml)
└── tests/                     # Pytest birim, entegrasyon ve canlı GPU smoke testleri
```

---

## 🛠️ Kurulum ve Çalıştırma Seçenekleri (Setup Options)

İhtiyacınıza göre iki farklı çalışma modundan birini seçebilirsiniz:

### Seçenek A: Demo / Hafif Mod (Hızlı Doğrulama ve Kod İncelemesi)
> **Model İndirmesi Gerektirmez (~0 MB İndirme):** Deterministik anlamsal fallback ve kural tabanlı moderasyon kullanır. CI ve hızlı arayüz testi için idealdir.

```bash
# 1. Depoyu klonlayın
git clone https://github.com/CALISKAN-EMRE/NSOSYAL.git
cd NSOSYAL

# 2. Backend ortamını kurun
cd backend
python -m venv .venv

# Windows Powershell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# 3. Demo modunda başlatın (Kök dizinden tek komutla: scripts/run_demo.bat veya .sh)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# (Veya SEMANTIC_MODE=demo ortam değişkeniyle)
```

---

### Seçenek B: Tam ML Modu (Üretim Yapay Zekâ Mimarisi)
> **Gerçek Türkçe Transformer Modellerini Yükler:** ModernBERT-TR (Kümeleme + Reranker + Guardrail) ve Multilingual-E5 (Arama) modelleri yerel GPU/CPU üzerinde çalışır.

```bash
# 1. Backend ML bağımlılıklarını yükleyin
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # (Linux/macOS: source .venv/bin/activate)

# NVIDIA GPU / CUDA hızlandırması için (Örnek: CUDA 12.4):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements-ml.txt

# (CPU üzerinde çalıştırmak için doğrudan):
# pip install -r requirements-ml.txt

# 2. ML modunda başlatın (Kök dizinden tek komutla: scripts/run_ml.bat veya .sh)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

### 3. Frontend Arayüzünü Başlatma (Her İki Mod İçin Ortak)
Yeni bir terminalde:
```bash
cd frontend
npm install
npm run dev
```

* **Web Kullanıcı Arayüzü:** [http://localhost:3000](http://localhost:3000)
* **REST API Dokümantasyonu (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Sistem & ML Durum Uç Noktası:** [http://127.0.0.1:8000/api/system/status](http://127.0.0.1:8000/api/system/status)

---

## 🧪 Testleri Çalıştırma (Running Verification Tests)

```bash
# 1. Hızlı Regresyon Test Paketi (Pytest - Demo Modu):
python -m pytest tests -v

# 2. Canlı GPU ML Semantik Boru Hattı Doğrulama Testi:
python -m tests.smoke_test_ml_live

# 3. Canlı GPU Moderasyon & Kalibre Edilmiş Eşik Doğrulama Testi:
python -m tests.smoke_test_moderation_live

# 4. Frontend Üretim Derleme Testi:
cd frontend && npm run build
```

---

## ⚠️ Veri ve Entegrasyon Uyarısı (Important Disclosures)

1. **API Erişimi:** Bu proje bir TEKNOFEST 2026 yarışma prototipidir. Mevcut aşamada sistem **herhangi bir canlı/resmi NSosyal API'sine bağlı değildir** ve yetkisiz veri kazıma (scraping) yapılmamaktadır.
2. **Sentetik Veri:** Sistemde kullanılan paylaşımlar (`data/demo_posts.json`), prototipin yeteneklerini test etmek üzere kurgulanmış **sentetik Türkçe içeriklerdir**. Gerçek kişi veya kamu kurumları temsil edilmemektedir.
3. **Model Hakları ve Atıf:** Kullanılan modeller (`ytu-ce-cosmos/modernbert-tr-embed`, `ytu-ce-cosmos/modernbert-tr-reranker`, `ytu-ce-cosmos/modernbert-tr-guardrail`, `intfloat/multilingual-e5-large-instruct`) ilgili yazarların açık kaynak lisanslarına (Apache-2.0 / MIT) tabidir. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.
