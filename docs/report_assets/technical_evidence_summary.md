# NSosyal Pusula — Teknik Kanıt ve Değerlendirme Özeti
**TEKNOFEST 2026 Türkçe Doğal Dil İşleme Yarışması — Rapor Kanıt Paketi**

---

## 1. Doğrulanmış Donanım ve Çalışma Ortamı

Tüm yerel ölçümler, çıkarım süreleri, bellek tüketimleri ve testler aşağıdaki tekil ve doğrulanmış donanım platformu üzerinde gerçekleştirilmiştir:

* **İşlemci (CPU):** 13th Gen Intel(R) Core(TM) i5-13600KF (14 Çekirdek: 6 Performans + 8 Verimlilik, 20 İş Parçacığı)
* **Sistem Belleği (RAM):** 32.0 GB DDR5/DDR4 (31.82 GB kullanılabilir)
* **Grafik İşlemci (GPU):** NVIDIA GeForce RTX 3060 (Masaüstü, 12.0 GB GDDR6 VRAM)
* **İşletim Sistemi:** Microsoft Windows 11 Pro 64-bit (Build 26200)
* **CUDA Sürümü:** 12.4
* **PyTorch Sürümü:** 2.6.0+cu124 (CUDA Hızlandırmalı)
* **Python Sürümü:** 3.13.7
* **Frontend Çalışma Ortamı:** Node.js v20.x, Next.js 14.2.23 (React 18)
* **Backend Çalışma Ortamı:** FastAPI 0.115+, Uvicorn, Scikit-learn 1.6+

---

## 2. BÖLÜM A: Harici Olarak Yayınlanmış Resmi Karşılaştırma Kanıtları

*Bu tablodaki tüm metrikler, ilgili modellerin resmi model kartları veya TR-MTEB / MTEB liderlik tablolarından doğrudan alınmıştır; yerel ölçümlerle birleştirilmemiştir.*

| Model Tanımlayıcısı | Parametre Sayısı | Lisans | Görev / Benchmark | Resmi Yayınlanmış Skor | Birincil Kaynak / Model Kartı | Erişim Tarihi |
| :--- | :---: | :---: | :--- | :---: | :--- | :---: |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 149M | Apache-2.0 | TR-MTEB Clustering | **58.07** (Ortalama) | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 149M | Apache-2.0 | TR-MTEB Retrieval (nDCG@10) | **81.08** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 149M | Apache-2.0 | Guardrail-TR TEST (Unsafe F1) | **0.930** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 |
| **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 149M | Apache-2.0 | Guardrail-TR TEST (Weighted F1)| **0.886** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 |
| **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 149M | Apache-2.0 | Guardrail-TR TEST (AUPRC Macro) | **0.917** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 |
| **`intfloat/multilingual-e5-large-instruct`**| 560M | MIT | MTEB Multilingual Retrieval | **67.30** | [HuggingFace Model Card](https://huggingface.co/intfloat/multilingual-e5-large-instruct) | 2026-08-22 |
| **`intfloat/multilingual-e5-base`** | 278M | MIT | MTEB Multilingual Retrieval | **64.40** | [HuggingFace Model Card](https://huggingface.co/intfloat/multilingual-e5-base) | 2026-08-22 |

---

## 3. BÖLÜM B: Yerel Olarak Ölçülen ve Doğrulanan Deneysel Kanıtlar

*Aşağıdaki tüm metrikler, NVIDIA RTX 3060 GPU üzerinde projenin kendi kod tabanı ve veri setleri çalıştırılarak doğrudan ölçülmüştür.*

### 3.1. Gömme Modelleri Türkçe Kümeleme ve Çıkarım Karşılaştırması
*Kaynak Veri:* [`docs/report_assets/data/embedding_comparison.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/embedding_comparison.csv)  
*Grafik Varlığı:* [`docs/report_assets/charts/chart_a_embedding_model_comparison.png`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/charts/chart_a_embedding_model_comparison.png)

| Model ID | Parametre | HDBSCAN NMI | HDBSCAN ARI | Çıkarım Gecikmesi (ms/metin) | Model VRAM (GB) | Mimari Rolü |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | **149M** | **0.8148** | **0.6720** | **1.70 ms** | **0.58 GB** | **Seçilen Birincil Kümeleme & Bağlam Gömme Modeli** |
| `intfloat/multilingual-e5-large-instruct` | 560M | 0.7712 | 0.5980 | 6.96 ms | 2.15 GB | Seçilen Serbest Metin Semantik Arama Modeli |
| `intfloat/multilingual-e5-base` | 278M | 0.7289 | 0.5340 | 2.37 ms | 1.07 GB | Hafif Çok Dilli Yedek Model |
| `paraphrase-multilingual-mpnet-base-v2` | 278M | 0.6974 | 0.4810 | 2.45 ms | 1.07 GB | Genel Çok Dilli Karşılaştırma Modeli |
| `bert-base-turkish-cased-mean-nli-stsb-tr`| 110M | 0.6120 | 0.3950 | 2.21 ms | 0.44 GB | Klasik BERT Türkçe Karşılaştırma Modeli |
| `ytu-ce-cosmos/turkish-base-bert-uncased` | 110M | 0.4985 | 0.2810 | 2.23 ms | 0.44 GB | Temel BERT Karşılaştırma Modeli |

### 3.2. Anlamsal Kümeleme ve Başlıklandırma Kalite İlerlemesi (Hardening)
*Kaynak Veri:* [`docs/report_assets/data/semantic_hardening_comparison.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/semantic_hardening_comparison.csv)  
*Grafik Varlığı:* [`docs/report_assets/charts/chart_b_semantic_hardening_progression.png`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/charts/chart_b_semantic_hardening_progression.svg)

| Geliştirme Aşaması | Örneklem | Keşfedilen Küme | NMI Skoru | ARI Skoru | V-Measure | Aykırı Değer Oranı | Başlıklandırma Yöntemi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Faz 2B İlk Canlı Çıktı (Ham Demo)** | 12 Gönderi | 2 Küme | 0.5210 | 0.3120 | 0.5210 | %33.3 | Statik / Ham Kelime Birleştirme ("Bedava & Http & Yapay") |
| **Faz 2B Güçlendirilmiş (Hardened)** | 50 Gönderi | 9 Küme | **0.8086** | **0.6591** | **0.8086** | **%0.0** | **Dinamik c-TF-IDF Ayırt Edici N-Gram Formülasyonu** |

### 3.3. ModernBERT-TR-Guardrail Yerel TEST Kümesi Değerlendirmesi
*Kapsam:* `ytu-ce-cosmos/guardrail-tr` veri setinin (~405.000 toplam satır) resmi **held-out TEST ayrımından örneklenen 1.000 satırlık alt küme**.  
*Kaynak Veri:* [`docs/report_assets/data/guardrail_test_evaluation.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/guardrail_test_evaluation.csv)  
*Grafik Varlığı:* [`docs/report_assets/charts/chart_c_guardrail_test_evaluation.png`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/charts/chart_c_guardrail_test_evaluation.svg)  
*Çıkarım Hızı:* **23.35 ms / örnek** (RTX 3060 CUDA, batch_size=32).

| Tehlike Sınıfı | Kullanılan Eşik ($\tau$) | Yerel Test Precision | Yerel Test Recall | Yerel Test F1-Skoru | Pozitif Destek (Örnek Sayısı) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`unsafe` (Genel Güvensizlik)** | `0.55` | **0.9663** | **0.9107** | **0.9377** | 504 |
| **`SEXUAL_CONTENT_ADULT`** | `0.50` | **0.8923** | **0.9508** | **0.9206** | 61 |
| **`SELF_HARM_SUICIDE`** | `0.85` | **0.9020** | **0.8846** | **0.8932** | 52 |
| **`HARASSMENT_OFFENSIVE`** | `0.80` | **0.8786** | **0.9005** | **0.8894** | 201 |
| **`PRIVACY_VIOLATION`** | `0.80` | **0.8929** | **0.8621** | **0.8772** | 29 |
| **`HATE_DISCRIMINATION`** | `0.65` | **0.8417** | **0.8632** | **0.8523** | 117 |
| **`INJECTION_JAILBREAK`** | `0.45` | **0.7843** | **0.8889** | **0.8333** | 45 |
| **`VIOLENT_CRIMES`** | `0.80` | **0.7797** | **0.7797** | **0.7797** | 59 |
| **`NON_VIOLENT_CRIMES`** | `0.30` | **0.7049** | **0.8600** | **0.7748** | 50 |
| **`CSAE` (Çocuk İstismarı)** | `0.85` | **0.7500** | **0.7500** | **0.7500** | 20 |
| **`MISINFORMATION_POLITICAL`** | `0.35` | **0.7273** | **0.7619** | **0.7442** | 21 |
| **Makro Ortalama (Macro-F1)** | — | **0.8198** | **0.8521** | **0.8315** | — |
| **Ağırlıklı Ortalama (Weighted-F1)** | — | **0.8482** | **0.8670** | **0.8541** | 654 |

### 3.4. Karar Eşiği Kalibrasyonu (Yalnızca DEV Ayrımı)
*Kapsam:* `ytu-ce-cosmos/guardrail-tr` veri setinin resmi **validation (DEV) ayrımından örneklenen 1.000 satırlık alt küme**. Test kümesine kalibrasyon sürecinde asla dokunulmamıştır.  
*Kaynak Veri:* [`docs/report_assets/data/threshold_calibration.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/threshold_calibration.csv)  
*Grafik Varlığı:* [`docs/report_assets/charts/chart_d_threshold_calibration.png`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/charts/chart_d_threshold_calibration.svg)

### 3.5. Bağlam Kaynağı Arama & Cross-Encoder Yeniden Sıralama (Reranker) Ablasyonu
*Kaynak Veri:* [`docs/report_assets/data/retrieval_reranker_ablation.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/retrieval_reranker_ablation.csv)  
*Grafik Varlığı:* [`docs/report_assets/charts/chart_e_reranker_ablation.png`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/charts/chart_e_reranker_ablation.svg)

* **ModernBERT Yoğun Arama (Dense):** nDCG@10: `0.9758` $\to$ **ModernBERT Cross-Encoder Sonrası:** nDCG@10: `0.9873` (**+0.0115 Kazanç**, Gecikme: 51.06 ms).
* **Multilingual-E5-Large-Instruct Yoğun Arama:** nDCG@10: `0.9967` $\to$ **ModernBERT Cross-Encoder Sonrası:** nDCG@10: `0.9841` (**-0.0126 Negatif Transfer**).
* *Mimari Karar:* Cross-Encoder reranker modeli yalnızca kendi eğitim dağılımıyla uyumlu olan ModernBERT aday havuzuna uygulanmış, mE5 serbest metin arama hattında negatif transferi önlemek amacıyla devre dışı bırakılmıştır.

---

## 4. BÖLÜM C: Kontrollü Sentetik Sosyal Medya Sanity Testleri

*Kapsam:* Türkçe sosyal medya dil dinamiklerini (hakaret, taciz, spam linkler, büyük harf bağırma, koordineli şablon paylaşımlar) temsil eden 12 kontrollü test senaryosu.  
*Kaynak Veri:* [`docs/report_assets/data/controlled_sanity_results.csv`](file:///c:/Users/3rcal/OneDrive/Masa%C3%BCst%C3%BC/NSOSYAL/docs/report_assets/data/controlled_sanity_results.csv)

* **Başarı Durumu:** **12 / 12 Kontrollü Sanity Senaryosu Başarıyla Geçti (%100.0 Başarı Oranı)**
  - 4/4 Yapıcı/Güvenli Gönderi $\to$ `Review Priority: LOW`, İnsan İncelemesi Önerilmedi (Temiz).
  - 2/2 Ağır Taciz & Hakaret $\to$ `Review Priority: HIGH`, `HARASSMENT_OFFENSIVE` tetiklendi.
  - 1/1 Şiddet Tehdidi / Nefret Riski $\to$ `Review Priority: CRITICAL`, `VIOLENT_CRIMES` tetiklendi.
  - 2/2 Spam Bağlantı ve Kripto Airdrop $\to$ `Review Priority: HIGH`, `Spam Skoru >= 0.90` tetiklendi.
  - 3/3 Çoklu Hesap Eşzamanlı Şablon Paylaşımı $\to$ `Review Priority: HIGH`, `Tekrar Skoru = 0.90` ve koordinasyon sinyali tetiklendi.

---

## 5. BÖLÜM D: Sistem Bütünlüğü, Test ve Derleme Metrikleri

* **Birim & Entegrasyon Testleri:** `python -m pytest tests -v` $\to$ **37 / 37 Test Başarılı (100% Yeşil)**, Çalışma Süresi: **4.12 saniye**.
* **Next.js Frontend Üretim Derlemesi:** `npm run build` $\to$ **4/4 Statik Rota Hatasız Derlendi**, 0 TypeScript / JSX hatası.
* **Canlı API Uçtan Uca Yanıt Süreleri (RTX 3060 CUDA):**
  - `GET /health` $\to$ **< 5 ms**
  - `GET /api/topics` (HDBSCAN Kümeleme) $\to$ **30 - 45 ms**
  - `GET /api/context/{topic_id}` (Dense Retrieval + Reranking) $\to$ **320 - 350 ms**
  - `POST /api/safety/analyze` (ModernBERT Guardrail + Spam/Coordination Füzyonu) $\to$ **30 - 45 ms**
  - `GET /api/search?q=...` (mE5-Large-Instruct Semantik Arama) $\to$ **480 - 520 ms**
  - `GET /api/recommendations` (Açıklanabilir Öneri & Ceza Hesaplama) $\to$ **15 - 25 ms**

---

## 6. BÖLÜM E: Mevcut Mühendislik ve Bilimsel Sınırlar (Limitations)

1. **LLM Kullanılmaması:** Sistem, jeneratif hallucination risklerini ve yüksek hesaplama maliyetlerini önlemek amacıyla LLM (Üretken Büyük Dil Modeli) içermez; sınıflandırma ve yoğun gömme modellerine dayanır.
2. **Nihai Yargı İddiasında Bulunmama:** Moderasyon motoru hiçbir içeriği kesin olarak "yasadışı", "ırkçı", "bot" veya "dezenformasyon" olarak etiketlemez; yalnızca açıklanabilir *Risk Göstergesi* ve *İnceleme Önerisi* üretir.
3. **Sentetik Veri Kapsamı:** Demonstrasyon külliyatı (70 gönderi) ve kontrollü sanity seti (12 senaryo), organik Twitter/NSosyal platform trafiği değil, projenin çok boyutlu mimarisini doğrulamak üzere hazırlanmış sentetik örneklemlerdir.
4. **Guardrail-TR Alt Küme Ölçümü:** Guardrail modeli, ~405 bin satırlık tam külliyatın donanım sınırları dahilinde temsil gücü yüksek 1.000 satırlık DEV ve 1.000 satırlık TEST örneklemleri üzerinde yerel olarak doğrulanmıştır.
