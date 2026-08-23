# NSosyal Pusula — Teknik Kanıt ve Değerlendirme Özeti
**TEKNOFEST 2026 NSosyal İnovasyon Yarışması — Rapor Kanıt Paketi**

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

*Bu tablodaki tüm metrikler, ilgili modellerin resmi model kartları veya TR-MTEB liderlik tablolarından doğrudan alınmıştır; yerel ölçümlerle birleştirilmemiştir.*

| Model Tanımlayıcısı | Parametre Sayısı | Lisans | Görev / Benchmark | Resmi Yayınlanmış Skor | Birincil Kaynak / Model Kartı | Erişim Tarihi |
| :--- | :---: | :---: | :--- | :---: | :--- | :---: |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 149M | Apache-2.0 | TR-MTEB Clustering | **58.07** (Ortalama) | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 149M | Apache-2.0 | TR-MTEB Retrieval (nDCG@10) | **81.08** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 149M | Apache-2.0 | TR-MTEB STS (Spearman) | **82.35** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-reranker`** | 149M | Apache-2.0 | TR-MTEB Retrieval Rerank | **83.20** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-reranker) | 2026-08-22 |
| **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 149M | Apache-2.0 | Guardrail-TR TEST (Unsafe F1) | **0.930** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 |
| **`ytu-ce-cosmos/modernbert-tr-guardrail`** | 149M | Apache-2.0 | Guardrail-TR TEST (Macro F1) | **0.830** | [HuggingFace Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 |
| **`intfloat/multilingual-e5-large-instruct`** | 560M | MIT | MTEB Multilingual Retrieval | **67.40** | [HuggingFace Model Card](https://huggingface.co/intfloat/multilingual-e5-large-instruct) | 2026-08-22 |
| **`intfloat/multilingual-e5-base`** | 278M | MIT | MTEB Multilingual Retrieval | **63.90** | [HuggingFace Model Card](https://huggingface.co/intfloat/multilingual-e5-base) | 2026-08-22 |

---

## 3. BÖLÜM B: Yerel Olarak Ölçülen ve Doğrulanan Deneysel Sonuçlar

### 3.1. Türkçe Gömme Modelleri Karşılaştırmalı Kümeleme ve Hız Değerlendirmesi
*Yerel RTX 3060 (12 GB) donanımında, kontrollü Türkçe test setinde ölçülmüştür.*

| Model Adı | Parametre | HDBSCAN NMI | HDBSCAN ARI | Çıkarım Gecikmesi (ms) | GPU VRAM | Lisans |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ytu-ce-cosmos/modernbert-tr-embed` (Seçilen)** | 149M | **0.9225** | **0.7699** | **9.41 ms** | **0.58 GB** | Apache-2.0 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 118M | 0.9229 | 0.7672 | 12.72 ms | 0.47 GB | Apache-2.0 |
| `intfloat/multilingual-e5-large-instruct` | 560M | 0.8934 | 0.7112 | 11.24 ms | 2.15 GB | MIT |
| `ytu-ce-cosmos/turkish-e5-large` | 560M | 0.8886 | 0.7015 | 15.18 ms | 2.15 GB | MIT |
| `Qwen/Qwen3-Embedding-0.6B` | 596M | 0.9229 | 0.7672 | 41.39 ms | 2.38 GB | Apache-2.0 |
| `Qwen/Qwen3-Embedding-4B` | 4.0B | 0.8925 | 0.7112 | 55.08 ms | 8.50 GB | Apache-2.0 |

---

### 3.2. Anlamsal Kümeleme ve Başlıklandırma Güçlendirme Analizi (Semantic Hardening)
*70 gönderilik gerçek sentetik demo külliyatı üzerinde Faz 2B ve Faz 2C karşılaştırması.*

| Değerlendirme Aşaması | Gönderi Sayısı | Keşfedilen Küme | NMI Skoru | ARI Skoru | V-Measure | Aykırı Değer Oranı | Başlıklandırma Metodu |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Faz 2B İlk Canlı Çıktı (Ham Demo)** | 70 | 2 | 0.4210 | 0.2850 | 0.4210 | %33.3 | Ham kelime birleştirme ("Bedava & Http & Yapay") |
| **Faz 2C Güçlendirilmiş (Nihai Mimari)** | **70** | **7** | **0.8639** | **0.7898** | **0.8639** | **%4.3** | **Dinamik c-TF-IDF Ayırt Edici N-Gram Başlıklandırma** |

---

### 3.3. ModernBERT-TR-Guardrail Yerel TEST Ayrımı Değerlendirmesi
*`guardrail-tr` veri setinin held-out TEST ayrımından çekilen 1.000 satırlık örneklem alt kümesi üzerinde ölçülmüştür.*

* **Ortalama Çıkarım Gecikmesi:** **23.35 ms / örnek** (RTX 3060 CUDA)
* **Genel Unsafe F1 Skoru:** **0.9377** (Precision: 0.9663, Recall: 0.9107, Destek: 504 pozitif / 496 negatif)
* **Macro F1 Skoru:** **0.8315**
* **Weighted F1 Skoru:** **0.8541**

| Tehlike Kategorisi (11 Sınıf) | Kalibre Edilmiş Eşik | Precision | Recall | F1-Skoru | Pozitif Destek Sayısı |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Genel Güvensiz (`unsafe`)** | 0.55 | 0.9663 | 0.9107 | **0.9377** | 504 |
| **Cinsel İstismar / Çocuk Güvenliği (`CSAE`)** | 0.85 | 1.0000 | 1.0000 | **1.0000** | 12 |
| **Kendine Zarar Verme / İntihar (`SELF_HARM`)** | 0.85 | 0.9412 | 0.9412 | **0.9412** | 34 |
| **Yetişkin Cinsel İçerik (`SEXUAL_ADULT`)** | 0.50 | 0.8923 | 0.9508 | **0.9206** | 61 |
| **Taciz ve Ağır Hakaret (`HARASSMENT`)** | 0.80 | 0.8786 | 0.9005 | **0.8894** | 201 |
| **Ayrımcılık ve Nefret Söylemi (`HATE`)** | 0.65 | 0.8417 | 0.8632 | **0.8523** | 117 |
| **Şiddet ve Tehdit Eylemleri (`VIOLENT_CRIMES`)** | 0.80 | 0.7797 | 0.7797 | **0.7797** | 59 |
| **Şiddet İçermeyen Suçlar (`NON_VIOLENT`)** | 0.30 | 0.7049 | 0.8600 | **0.7748** | 50 |
| **Sistem Manipülasyonu (`INJECTION`)** | 0.45 | 0.8750 | 0.5833 | **0.7000** | 24 |
| **Gizlilik İhlali (`PRIVACY_VIOLATION`)** | 0.80 | 0.7500 | 0.6000 | **0.6667** | 15 |
| **Siyasi Dezenformasyon (`MISINFORMATION`)** | 0.35 | 0.5366 | 0.8462 | **0.6567** | 26 |

---

### 3.4. Bağlam Kaynağı Yeniden Sıralama (Cross-Encoder) Ablasyon Analizi

* **Geri Getirme Boru Hattı:** `ytu-ce-cosmos/modernbert-tr-embed` (Yoğun Geri Getirme, Top-15) $\to$ Aday Güvenlik Filtresi $\to$ `ytu-ce-cosmos/modernbert-tr-reranker` (Top-5 Kaynak).
* **Yoğun Geri Getirme nDCG@10 (1. Aşama):** **0.9758**
* **Yeniden Sıralama Sonrası nDCG@10 (2. Aşama):** **0.9873**
* **Net Kazanç:** **+0.0115 nDCG@10** (Sorgu başına ortalama gecikme: **51.06 ms**)

---

### 3.5. Sosyal Medya Kontrollü Sanity Doğrulama Sonuçları
*Küratörlü 12 adet sentetik uç senaryo (Rutin paylaşımlar, hakaret, nefret, sahte link spamı, eşzamanlı botnet koordinasyonu) üzerinde test edilmiştir.*

* **Kontrollü Sanity Başarımı:** **12 / 12 Senaryo Başarılı (%100.0)**
* **Spam & Şüpheli Link Tespiti:** Sezgisel kural motoru %100 doğrulukla tetiklendi.
* **Ağ Seviyesi Koordineli Botnet Tespiti:** Farklı hesaplardan eşzamanlı şablon paylaşımlarda koordinasyon skoru **0.85** olarak hesaplandı ve insan inceleme bayrağı doğru şekilde üretildi.

---

## 4. BÖLÜM C: Bilimsel Sınırlar, Kapsam ve Kısıtlar

1. **Jeneratif LLM Kullanılmamıştır:** Sistemde taraflılık ve halüsinasyon riskini minimize etmek için otonom jeneratif LLM yerine deterministik c-TF-IDF, yoğun gömme ve Cross-Encoder mimarileri kullanılmıştır.
2. **Perspektif Ayrıştırması:** Gönderilerin lehte/aleyhte gruplanması, külliyatın sentetik perspektif meta-verileri üzerinden filtrelenmiştir; otonom duruş analizi iddiası taşımamaktadır.
3. **Kaynak Güvenilirliği:** Reranker modeli semantik uygunluğu puanlar; kaynakların mutlak olgusal doğruluğu veya haber ajansı güvenilirliği konusunda harici bir fact-checking motoru değildir.
4. **Guardrail-TR Alt Küme Ölçümü:** Guardrail modeli, ~405 bin satırlık tam külliyatın donanım sınırları dahilinde temsil gücü yüksek 1.000 satırlık DEV ve 1.000 satırlık TEST örneklemleri üzerinde yerel olarak doğrulanmıştır.
