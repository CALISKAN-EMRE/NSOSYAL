# NSosyal Pusula — Faz 2A Bilimsel Dürüstlük ve Model Doğrulama Denetim Raporu
## Scientific Integrity Audit & Methodology Validation

Bu doküman, Faz 2A model seçim sürecinde yapılan denetimleri, giderilen metodolojik hataları ve iki aşamalı erişim/reranking bulgularını kayıt altına alır.

---

## 1. Düzeltilen İddialar ve Metodolojik İyileştirmeler

1. **Harici Puanların Temizlenmesi:**
   * Resmi model kartlarında açıkça yer almayan tüm tahmini/türetilmiş puanlar kaldırılmıştır.
   * Yalnızca yazar model kartlarında ve resmi MTEB liderlik tablolarında kayıtlı olan doğrulanabilir birincil kaynak verileri muhafaza edilmiştir.
2. **Erişim Doygunluğunun Giderilmesi ve İki Aşamalı Reranking:**
   * Korpus 50 dokümana genişletilmiş; aynı anahtar kelimeleri içeren ama alakasız/zıt olan 25 adet zorlu negatif eklenmiştir.
   * `ytu-ce-cosmos/modernbert-tr-reranker` Cross-Encoder modeli ile iki aşamalı (First-stage dense + Second-stage rerank) erişim test edilmiş; ModernBERT ikilisinde nDCG@10 skoru **0.9758'den 0.9873'e** yükselmiştir.
3. **Kümeleme Sonuçlarının Objektif Değerlendirilmesi:**
   * Sentetik `topic_hint` kural bazı `oracle_metadata_grouping` (Denetimli Üst Sınır) olarak yeniden etiketlenmiş; yarışmalı değerlendirmeden çıkarılmıştır.
   * Gerçek denetimsiz `TF-IDF + Spherical K-Means` bazı (NMI=0.8575, ARI=0.6861) ile karşılaştırma yapılmıştır.
   * HDBSCAN kümelemesinde `ytu-ce-cosmos/modernbert-tr-embed` (0.9225 NMI) ve `Qwen3-0.6B` (0.9229 NMI) modelleri yüksek anlamsal yoğunluk ayrışması göstermiştir.
4. **Donanım ve Bellek Şeffaflığı:**
   * `Qwen3-Embedding-8B` modelinin 12 GB VRAM donanımında fiziksel belleği aşarak Windows Unified Memory / PCIe üzerinden **+3.88 GB sistem RAM'ine taştığı** ve 847 ms gecikmeye yol açtığı belgelenmiştir.
   * `Qwen3-Embedding-4B` modelinin 7.55 GB VRAM ile 12 GB GPU'da tamamen yerel çalıştığı (55 ms gecikme) tespit edilmiştir.

---

## 2. Kanıt Kaynağı Sınıflandırması (Provenance Table)

| İddia / Veri Alanı | Kaynak Türü | Doğrulama Yöntemi / Birincil Kaynak |
| :--- | :--- | :--- |
| Model Lisansları | Harici Birincil Kaynak | Hugging Face Hub `model_info.cardData.license` |
| Qwen3-8B MTEB Skoru (70.58) | Harici Birincil Kaynak | [Qwen3-Embedding-8B Model Card](https://huggingface.co/Qwen/Qwen3-Embedding-8B) |
| ModernBERT TR-MTEB Skorları | Harici Birincil Kaynak | [ModernBERT-TR-Embed Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-embed) |
| ModernBERT Reranker TR-MTEB Skorları | Harici Birincil Kaynak | [ModernBERT-TR-Reranker Model Card](https://huggingface.co/ytu-ce-cosmos/modernbert-tr-reranker) |
| CUDA VRAM & RAM Ölçümleri | Yerel Ölçüm | RTX 3060 (12 GB VRAM) PyTorch CUDA runtime (`torch.cuda.memory_allocated`) |
| Tekil Cümle ve Rerank Gecikmeleri | Yerel Ölçüm | 20-30 iterasyon ortalaması (`time.perf_counter`) |
| STS Spearman ρ & Pearson r | Yerel Ölçüm | 32 çiftlik NSosyal Türkçe STS veri seti |
| HDBSCAN & KMeans Metrikleri | Yerel Ölçüm | 40 örnekli 6 sınıflı NSosyal Kümeleme korpusu |
| İki Aşamalı Erişim (nDCG@10, MRR@10) | Yerel Ölçüm | 50 dokümanlık zorlu negatifli NSosyal Erişim korpusu |