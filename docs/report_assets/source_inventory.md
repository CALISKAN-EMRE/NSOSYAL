# NSosyal Pusula — Kaynakça ve Atıf Envanteri (Source Inventory)
**TEKNOFEST 2026 Türkçe Doğal Dil İşleme Yarışması — Resmi Model, Veri Seti ve Literatür Envanteri**

---

## 1. Kullanılan Temel Modeller ve Veri Setleri

| # | Kaynak Başlığı | Yazar / Kurum | Resmi URL | Erişim Tarihi | Desteklediği Teknik İddia / Kullanım Alanı |
| :-: | :--- | :--- | :--- | :-: | :--- |
| **1** | **`ytu-ce-cosmos/modernbert-tr-embed`** | Yıldız Teknik Üniversitesi Bilgisayar Mühendisliği (COSMOS NLP Grubu) | [HuggingFace: modernbert-tr-embed](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) | 2026-08-22 | Türkçe sosyal medya gönderilerinin anlamsal temsili ve yoğun vektör kümelemesi için seçilen birincil gömme modeli (149M parametre, 768d, Apache-2.0). |
| **2** | **`ytu-ce-cosmos/modernbert-tr-reranker`** | Yıldız Teknik Üniversitesi Bilgisayar Mühendisliği (COSMOS NLP Grubu) | [HuggingFace: modernbert-tr-reranker](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-reranker) | 2026-08-22 | Bağlam Kartı için ilk aşama yoğun arama adayları arasından en güvenilir ve alakalı kaynakların yeniden sıralanması (Cross-Encoder, nDCG@10: 0.9873, Apache-2.0). |
| **3** | **`ytu-ce-cosmos/modernbert-tr-guardrail`** | Yıldız Teknik Üniversitesi Bilgisayar Mühendisliği (COSMOS NLP Grubu) | [HuggingFace: modernbert-tr-guardrail](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-guardrail) | 2026-08-23 | Türkçe içerik güvenliği, nefret söylemi, taciz, şiddet ve istismar risk sinyallerinin 11 sınıflı çok etiketli tespiti (149M parametre, Apache-2.0). |
| **4** | **`ytu-ce-cosmos/guardrail-tr`** | Yıldız Teknik Üniversitesi Bilgisayar Mühendisliği (COSMOS NLP Grubu) | [HuggingFace: guardrail-tr](https://huggingface.co/datasets/ytu-ce-cosmos/guardrail-tr) | 2026-08-23 | Moderasyon karar eşiklerinin kalibrasyonu (DEV ayrımı) ve yerel F1-skoru doğrulaması (TEST ayrımı) için kullanılan ~405K satırlık Türkçe güvenlik veri seti. |
| **5** | **`intfloat/multilingual-e5-large-instruct`** | Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, Furu Wei (Microsoft Research) | [HuggingFace: multilingual-e5-large-instruct](https://huggingface.co/intfloat/multilingual-e5-large-instruct) | 2026-08-22 | Doğal dil serbest sorgularla semantik arama yapılması için kullanılan asimetrik talimat tabanlı çok dilli model (560M parametre, MIT). |
| **6** | **`intfloat/multilingual-e5-base`** | Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder, Furu Wei (Microsoft Research) | [HuggingFace: multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base) | 2026-08-22 | Düşük kaynaklı donanımlarda veya CPU fallback modunda kullanılabilen hafif çok dilli alternatif model (278M parametre, MIT). |

---

## 2. Akademik Literatür ve Metodolojik Referanslar

| # | Akademik Eser / Kaynak | Yazarlar | Yayın / Konferans / ArXiv | URL | Desteklediği Metodoloji |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **7** | **ModernBERT: Smarter, Better, Faster, Longer** | Benjamin Warner, Antoine Chaffin, Benjamin Clavié, Orion Weller, Oskar Hallström, Nicolas Patry et al. | arXiv:2412.13663 (Answer.AI, LightOn, Hugging Face), 2024 | [arXiv:2412.13663](https://arxiv.org/abs/2412.13663) | 8192 token bağlam uzunluğu, FlashAttention-2 ve RoPE destekleyen modern encoder mimarisi temeli. |
| **8** | **Density-Based Clustering Based on Hierarchical Density Estimates (HDBSCAN)** | Ricardo J. G. B. Campello, Davoud Moulavi, Jörg Sander | Advances in Knowledge Discovery and Data Mining (PAKDD 2013), Springer | [Springer Link](https://doi.org/10.1007/978-3-642-37456-2_14) | Kümelerin önceden belirlenmiş sabit k sayısı olmadan yoğunluk tabanlı hiyerarşik keşfi ve aykırı değer izolasyonu. |
| **9** | **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks** | Nils Reimers, Iryna Gurevych | EMNLP 2019 | [ACL Anthology](https://aclanthology.org/D19-1410/) | Cümle ve paragraf seviyesinde anlamsal benzerlik ve yoğun vektör uzayı hesaplama metodolojisi. |
| **10** | **MTEB: Massive Text Embedding Benchmark** | Niklas Muennighoff, Nouamane Tazi, Loïc Magne, Nils Reimers | EACL 2023 | [ACL Anthology](https://aclanthology.org/2023.eacl-main.148/) | Çok dilli ve Türkçe gömme modellerinin sınıflandırma, kümeleme ve bilgi getirme liderlik tablosu standardı. |
| **11** | **TR-MTEB: Turkish Massive Text Embedding Benchmark** | Yıldız Teknik Üniversitesi COSMOS Grubu & Topluluk | HuggingFace TR-MTEB Leaderboard | [TR-MTEB Leaderboard](https://huggingface.co/spaces/ytu-ce-cosmos/Turkish_MTEB) | Türkçe doğal dil işleme görevlerinde gömme ve kümeleme performansının bağımsız karşılaştırma kriteri. |
