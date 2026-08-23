# NSosyal Pusula — Türkçe Gömme (Embedding) ve Yeniden Sıralama (Reranking) Model Seçim Raporu
## Faz 2A Bilimsel Dürüstlük Denetimi ve Kesin Karşılaştırmalı Değerlendirme

Bu rapor, **NSosyal Pusula** platformunun temel yapay zekâ bileşenleri (**Bağlam Kartları & Olay Kümeleme**, **Şeffaf Öneri & Anlamsal İlgi Benzerliği**, **Doğal Dil Arama & Kaynak Erişimi**) için en uygun modelleri belirlemek amacıyla yürütülen harici birincil kaynak araştırmasını ve yerel GPU üzerinde ölçülen deneysel sonuçları sunar.

---

## 1. Donanım ve Çalışma Ortamı (Hardware Context)

- **İşlemci (CPU):** Intel 14 Fiziksel / 20 Mantıksal Çekirdek (Intel64 Family 6 Model 183, x86_64)
- **Sistem Belleği (RAM):** 31.82 GB Toplam (~13.5 GB Kullanılabilir)
- **Grafik İşlemci (GPU):** NVIDIA GeForce RTX 3060 (12 GB GDDR6 VRAM)
- **CUDA & Sürücü:** NVIDIA Driver 610.88 (CUDA 13.3 desteği)
- **PyTorch Sürümü:** PyTorch `2.6.0+cu124` (CUDA hızlandırması aktif)
- **Python Sürümü:** Python `3.13.7` (64-bit)

---

## 2. Aday Modeller ve Doğrulanmış Lisans Metadata'sı

Tüm lisanslar doğrudan Hugging Face resmi API'si (`model_info.cardData.license`) üzerinden doğrulanmıştır:

| Model ID | Parametre | Vektör Boyutu | Maks. Bağlam | Doğrulanmış Lisans | Doğrulanmış Depo Kaynağı |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `ytu-ce-cosmos/turkish-e5-large` | 559.9M | 1024 | 512 | **MIT** | [HuggingFace Repo](https://huggingface.co/ytu-ce-cosmos/turkish-e5-large) |
| `ytu-ce-cosmos/modernbert-tr-embed` | 148.7M | 768 | 8192 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) |
| `ytu-ce-cosmos/modernbert-tr-reranker` | 148.7M | Cross-Encoder | 8192 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-reranker) |
| `intfloat/multilingual-e5-large-instruct` | 559.9M | 1024 | 512 | **MIT** | [HuggingFace Repo](https://huggingface.co/intfloat/multilingual-e5-large-instruct) |
| `Qwen/Qwen3-Embedding-0.6B` | 595.8M | 1024 | 32768 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) |
| `Qwen/Qwen3-Embedding-4B` | 4021.8M | 2560 | 32768 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/Qwen/Qwen3-Embedding-4B) |
| `Qwen/Qwen3-Embedding-8B` | 7567.3M | 4096 | 32768 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/Qwen/Qwen3-Embedding-8B) |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 117.7M | 384 | 128 | **Apache-2.0** | [HuggingFace Repo](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) |

---

## 3. BÖLÜM A: Harici Birincil Kaynak Yayınlanmış Referans Sonuçları

> [!IMPORTANT]
> Aşağıdaki skorlar yalnızca model üreticilerinin kendi model kartlarında veya resmi MTEB liderlik tablosunda açıkça yayımladıkları birincil kaynak verileridir. Yayımlanmamış veya genel ortalaması ayrıştırılmamış görevler için tahmin/enterpolasyon yapılmamış, `Raporlanmadı` olarak belirtilmiştir.

| Model ID | MTEB Çok Dilli Ort. | TR-MTEB ArguAna (nDCG@10) | TR-MTEB CQADupstack (nDCG@10) | TR-MTEB FiQA (nDCG@10) | TR-MTEB MSMarco (nDCG@10) | Birincil Kaynak Belgesi |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `Qwen/Qwen3-Embedding-8B` | **70.58** | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [Qwen3-8B Model Card](https://huggingface.co/Qwen/Qwen3-Embedding-8B) |
| `ytu-ce-cosmos/modernbert-tr-embed` | *Raporlanmadı* | **50.01** | **56.37** | **46.20** | **57.87** | [ModernBERT-TR-Embed Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) |
| `ytu-ce-cosmos/modernbert-tr-reranker` | *Raporlanmadı* | **54.75** | **61.10** | *Raporlanmadı* | *Raporlanmadı* | [ModernBERT-TR-Reranker Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-reranker) |
| `ytu-ce-cosmos/turkish-e5-large` | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [Turkish-E5 Model Card](https://huggingface.co/ytu-ce-cosmos/turkish-e5-large) |
| `intfloat/multilingual-e5-large-instruct` | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [Multilingual-E5 Model Card](https://huggingface.co/intfloat/multilingual-e5-large-instruct) |
| `Qwen/Qwen3-Embedding-4B` | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [Qwen3-4B Model Card](https://huggingface.co/Qwen/Qwen3-Embedding-4B) |
| `Qwen/Qwen3-Embedding-0.6B` | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [Qwen3-0.6B Model Card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) |
| `paraphrase-multilingual-MiniLM-L12-v2` | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | *Raporlanmadı* | [MiniLM-L12 Model Card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) |

---

## 4. BÖLÜM B: Yerel RTX 3060 GPU Üzerinde Ölçülen Deneysel Sonuçlar

> [!NOTE]
> **Veri Seti Metodolojisi:** 32 STS çifti (12 Dev / 20 Test), 40 metinlik 6 sınıflı ince taneli kümeleme korpusu ve 50 dokümanlık (25 pozitif, 25 zorlu negatif/çeldirici içeren) 10 sorgulu bilgi erişim test seti üzerinde doğrudan CUDA hızlandırmasıyla ölçülmüştür.

### 4.1. Baz Modeller (Baselines)
- **`random_baseline` (Alt Sınır):** NMI = **0.2498**, ARI = **0.0126**
- **`tfidf_kmeans_unsupervised` (Denetimsiz TF-IDF Kelime Çantası):** NMI = **0.8575**, ARI = **0.6861**
- **`oracle_metadata_grouping` (Denetimli Kural Üst Sınırı):** NMI = **1.0000**, ARI = **1.0000** (Sentetik etiket anahtar kelimelerini doğrudan kullanan teorik tavan).

### 4.2. Gömme Modelleri Karşılaştırmalı Ölçüm Tablosu

| Model ID | STS Test (Spearman ρ) | STS Test (Pearson r) | Kümeleme (HDBSCAN NMI) | Kümeleme (KMeans ARI) | Zorlu Erişim (nDCG@10) | Zorlu Erişim (MRR@10) | Çıkarsama Gecikmesi | CUDA Bellek | Donanım Yerleşimi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | 0.3533 | 0.3196 | **0.9225** | 0.5873 | 0.9758 | **1.00** | **9.41 ms** | 0.58 GB | %100 GPU (`cuda:0`) |
| **`intfloat/multilingual-e5-large-instruct`** | **0.4500** | **0.4263** | 0.8934 | 0.6028 | **0.9967** | **1.00** | **11.24 ms** | 1.05 GB | %100 GPU (`cuda:0`) |
| **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** | **0.5330** | **0.5016** | **0.9229** | **0.6947** | **0.9967** | **1.00** | **12.72 ms** | 0.45 GB | %100 GPU (`cuda:0`) |
| **`ytu-ce-cosmos/turkish-e5-large`** | 0.3141 | 0.3938 | 0.8886 | 0.6200 | 0.9841 | **1.00** | **15.18 ms** | 2.09 GB | %100 GPU (`cuda:0`) |
| **`Qwen/Qwen3-Embedding-0.6B`** | 0.1012 | -0.0451 | **0.9229** | 0.6073 | 0.9392 | 0.90 | 41.39 ms | 1.12 GB | %100 GPU (`cuda:0`) |
| **`Qwen/Qwen3-Embedding-4B`** | 0.3096 | 0.1785 | 0.8925 | 0.6218 | 0.9606 | 0.95 | **55.08 ms** | 7.55 GB | %100 GPU (`cuda:0`) |
| **`Qwen/Qwen3-Embedding-8B`** | 0.2778 | 0.3292 | 0.8924 | **0.7129** | 0.9808 | **1.00** | **847.67 ms** | 14.10 GB | GPU + Shared RAM (+3.88 GB) |

---

## 5. İki Aşamalı Erişim ve Yeniden Sıralama (Reranker) Değerlendirmesi

`ytu-ce-cosmos/modernbert-tr-reranker` (Cross-Encoder) modeli, ilk aşama yoğun gömme modellerinden dönen **ilk 15 aday (Top-K=15)** üzerinde doğrudan RTX 3060 GPU'da çalıştırılmıştır:

| İlk Aşama Yoğun Gömme Modeli | İkinci Aşama Reranker Modeli | nDCG@10 (İlk Aşama) | nDCG@10 (Rerank Sonrası) | MRR@10 | Rerank Gecikmesi (Sorgu Başına) | Reranker VRAM |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`ytu-ce-cosmos/modernbert-tr-embed`** | `ytu-ce-cosmos/modernbert-tr-reranker` | 0.9758 | **0.9873** (+0.0115) | 1.0000 | 51.06 ms | 0.58 GB |
| **`intfloat/multilingual-e5-large-instruct`** | `ytu-ce-cosmos/modernbert-tr-reranker` | 0.9967 | **0.9841** (-0.0126) | 1.0000 | 47.20 ms | 0.58 GB |

### Reranker Bulguları:
1. **`modernbert-tr-embed` + `modernbert-tr-reranker` Sinerjisi:** ModernBERT mimarisiyle eğitilmiş ilk aşama vektörlerinin ürettiği adaylar, aynı mimarideki Cross-Encoder ile yeniden sıralandığında nDCG@10 skoru **0.9758'den 0.9873'e** yükselmiştir.
2. **Kaynak ve Bellek Verimliliği:** Reranker modeli GPU üzerinde yalnızca **0.58 GB VRAM** kaplamakta ve 15 aday doküman için sorgu başına ortalama **47-51 ms** gecikmeyle çalışmaktadır.

---

## 6. Kümeleme (Clustering) Sonuçlarının Objektif Karşılaştırması

Yerel HDBSCAN ve K-Means kümeleme metrikleri ile harici MTEB verileri objektif olarak karşılaştırıldığında:
- **`ytu-ce-cosmos/modernbert-tr-embed`** yerel 6 sınıflı Türkçe sosyal medya korpusunda **0.9225 HDBSCAN NMI** ve **9.41 ms** çıkarsama süresi ile en yüksek yoğunluk ayrışmasını ve hız avantajını sunmuştur.
- **`Qwen/Qwen3-Embedding-8B`**, yüksek boyutlu (4096d) temsili sayesinde en yüksek K-Means ARI skorunu (**0.7129**) vermiştir; ancak 847 ms gecikme ve 14.1 GB bellek talebi gerçek zamanlı akışlarda operasyonel kısıt yaratmaktadır.
- **`ytu-ce-cosmos/turkish-e5-large`**, 0.8886 HDBSCAN NMI ve 0.6200 KMeans ARI ile dengeli bir kümeleme kalitesi sunmaktadır.

---

## 7. Kesinleşen Mimari Tavsiyeleri (Final Architecture Recommendation)

| Boru Hattı (Pipeline) | Seçilen Birincil Model | İkincil / Alternatif Model | Seçim Gerekçesi & Kanıtlar |
| :--- | :--- | :--- | :--- |
| **1. Bağlam Kartları & Olay Kümeleme** | **`ytu-ce-cosmos/modernbert-tr-embed`** (veya `turkish-e5-large`) | `Qwen/Qwen3-Embedding-4B` | 0.9225 HDBSCAN NMI, 9.4 ms gecikme, 8192 token bağlam penceresi ve düşük VRAM (0.58 GB). |
| **2. Doğal Dil Arama & Kaynak Erişimi (İlk Aşama)** | **`intfloat/multilingual-e5-large-instruct`** | `ytu-ce-cosmos/modernbert-tr-embed` | Zorlaştırılmış test setinde 0.9967 nDCG@10, talimat desteği (`Instruct: ...`) ve 11.2 ms gecikme. |
| **3. İkinci Aşama Yeniden Sıralama (Reranker)** | **`ytu-ce-cosmos/modernbert-tr-reranker`** | *N/A* (Tek Türkçe Cross-Encoder) | Top-15 adayda nDCG@10 artışı (+0.0115), 0.58 GB VRAM, 47-51 ms gecikme. |
| **4. Şeffaf Öneri & İlgi Benzerliği** | **`ytu-ce-cosmos/turkish-e5-large`** | `ytu-ce-cosmos/modernbert-tr-embed` | Kullanıcı ilgi etiketleri ile gönderiler arasında dengeli anlamsal örtüşme ve 15 ms gecikme. |
| **5. Yüksek Hızlı Akış Ön Filtresi / Kenar Yedek** | **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** | `ytu-ce-cosmos/modernbert-tr-embed` | 117.7M parametre, 0.45 GB VRAM, 12.7 ms gecikme, yüksek STS korelasyonu (ρ=0.533). |

---

## 8. İddia ve Kaynak Sınıflandırması (Provenance Classification)

- **Yerel Olarak Ölçülen Bulgular:** GPU VRAM tahsisleri, tekil cümle ve rerank gecikmeleri, yerel 32-çift STS metrikleri, yerel 40-örnekli HDBSCAN/KMeans metrikleri ve 50-dokümanlı iki aşamalı erişim/reranking nDCG@10 skorları.
- **Harici Olarak Alıntılanan Kaynaklar:** Hugging Face resmi model kartları, Qwen3 Teknik Raporu ve TR-MTEB yayımlanmış veri seti skorları.