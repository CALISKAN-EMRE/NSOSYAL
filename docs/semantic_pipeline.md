# NSosyal Pusula — Faz 2B Üretim Semantik Yapay Zekâ Dokümantasyonu
## Production Semantic Architecture & Pipeline Specifications

Bu doküman, **NSosyal Pusula** platformunun Faz 2B aşamasında üretime alınan yapay zekâ bileşenlerinin teknik mimarisini, kullanılan modelleri, seçim gerekçelerini, ampirik kanıtlarını ve operasyonel sınırlarını detaylandırır.

---

## 1. Bütünleşik Model Mimarisi ve Rol Dağılımı

| Boru Hattı | Seçilen Model | Model Tipi | Parametre & Boyut | Bağlam Penceresi | Doğrulanmış Lisans |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Olay & Konu Kümeleme** | `ytu-ce-cosmos/modernbert-tr-embed` | Bi-Encoder (Dense) | 148.7M (768d) | 8192 Token | **Apache-2.0** |
| **Bağlam Kaynak Erişimi (1. Aşama)** | `ytu-ce-cosmos/modernbert-tr-embed` | Bi-Encoder (Dense) | 148.7M (768d) | 8192 Token | **Apache-2.0** |
| **Bağlam Kaynak Reranker (2. Aşama)** | `ytu-ce-cosmos/modernbert-tr-reranker` | Cross-Encoder | 148.7M (Logits) | 8192 Token | **Apache-2.0** |
| **Doğal Dil Arama** | `intfloat/multilingual-e5-large-instruct` | Instruct Bi-Encoder | 559.9M (1024d) | 512 Token | **MIT** |
| **Şeffaf Öneri İlgi Benzerliği** | `ytu-ce-cosmos/modernbert-tr-embed` | Bi-Encoder (Dense) | 148.7M (768d) | 8192 Token | **Apache-2.0** |
| **Deterministik Yedek (Demo Modu)** | Demo Word-Hash / Heuristic | Baseline Algoritma | CPU | Sınırsız | **MIT** |

---

## 2. Model Seçim Gerekçeleri ve Ampirik Kanıtlar

### 2.1. Neden Kümeleme ve İlk Aşama Erişimde `modernbert-tr-embed`?
1. **Yerel HDBSCAN Başarısı:** Yerel 40 örnekli 6 sınıflı Türkçe sosyal medya kümeleme korpusunda **0.9225 HDBSCAN NMI** ve **0.7699 ARI** ile en yüksek küme saflığını sağlamıştır.
2. **Operasyonel Verimlilik:** Yalnızca **148.7M parametre** büyüklüğünde olup, tekil metin çıkarsama süresi **9.41 ms**, GPU VRAM ayak izi ise **0.58 GB** seviyesindedir.
3. **Geniş Bağlam:** Sosyal medya tartışma zincirlerini ve uzun haber metinlerini kesintiye uğratmadan işleyebilen **8192 token** bağlam penceresine sahiptir.

### 2.2. Neden İki Aşamalı Reranking'de `modernbert-tr-reranker`?
1. **Model Sinerjisi ve Doğruluk Artışı:** `modernbert-tr-embed` ilk aşama yoğun arama adayları ile eşleştirildiğinde nDCG@10 skoru **0.9758'den 0.9873'e (+0.0115)** yükselmiştir.
2. **Çapraz Dikkat Gücü (Cross-Attention):** Sorgu ve kaynak metinleri arasındaki ince anlamsal ilişkileri, olumsuzluk eklerini ve çeldiricileri bi-encoder'lara kıyasla daha keskin ayrıştırmaktadır.
3. **Düşük Kaynak Tüketimi:** GPU üzerinde yalnızca **0.58 GB VRAM** kaplamakta ve 15 aday için sorgu başına **47-51 ms** gecikmeyle çalışmaktadır.
4. *Not:* Bu reranker modeli, yerel deneylerimizde sıralama kalitesinde düşüş saptandığı için `multilingual-e5-large-instruct` ile otomatik olarak zincirlenmemiştir.

### 2.3. Neden Doğal Dil Aramada `multilingual-e5-large-instruct`?
1. **Talimat Tabanlı Erişim (Instruction-Tuned):** Model kartı tarafından şart koşulan resmi talimat formatı ile Türkçe arama sorgularını soru/istek bağlamında anlamlandırır:
   ```
   Instruct: Given a Turkish search query, retrieve relevant passages written in Turkish that best answer the query
   Query: <Kullanıcı Arama Sorgusu>
   ```
2. **Yüksek Erişim Doğruluğu:** 50 dokümanlık zorlu çeldiricili test setinde **0.9967 nDCG@10** ve **1.0000 MRR@10** üretmiştir.

---

## 3. Boru Hatları (Pipelines) ve İşleyiş

```
+---------------------------------------------------------------------------------------+
|                                    NSOSYAL PUSULA                                     |
|                            Faz 2B Semantik Zekâ Katmanı                               |
+---------------------------------------------------------------------------------------+
                                           |
         +---------------------------------+---------------------------------+
         |                                 |                                 |
         v                                 v                                 v
[1. Olay & Konu Kümeleme]     [2. İki Aşamalı Bağlam Kaynakları]   [3. Doğal Dil Arama]
  Gönderiler (Raw Texts)         Konu Başlığı & Özeti                 Kullanıcı Sorgusu (q)
         |                                 |                                 |
  ModernBERT-TR-Embed             ModernBERT-TR-Embed Dense          Multilingual-E5-Instruct
         |                                 | (Top-15 Aday)                   |
  L2 Normalizasyonu                        v                          Kosinüs Benzerlik Matrisi
         |                        ModernBERT-TR-Reranker                     |
      HDBSCAN                              | (Cross-Encoder)                 v
         |                                 v                          Sıralı Arama Sonuçları
  Dinamik Semantik Gruplar        Yeniden Sıralı Kaynaklar             (Relevance, Rank, Post)
  (Güven Skoru, Temsilciler)      (Relevance, Dense, Rank)
```

### 3.1. Şeffaf Öneri Motorunda Anlamsal İlgi Ayrışımı
Şeffaf öneri formülü, kullanıcının seçtiği ilgi alanları ile gönderi metni arasındaki vektör kosinüs yakınlığını `interest_match` faktöründe (ağırlık: 30) izole olarak kullanır. Algoritmanın geri kalanı (konu yakınlığı, güncellik, çeşitlilik, tekrar cezası, güvenlik cezası) tamamen şeffaf ve denetlenebilir kalır.

---

## 4. Çalışma Modları (Runtime Modes) ve Hata Toleransı

1. **`SEMANTIC_MODE=ml` (Varsayılan Üretim Modu):**
   * Modeller uygulama başlatılırken (`lifespan`) tek seferde belleğe yüklenir (`ModelManager` singleton).
   * Çıkarsamalar doğrudan NVIDIA GPU (`cuda:0`) üzerinde PyTorch hızlandırmasıyla çalışır.
   * Model yüklenmesinde donanım/bellek hatası oluşursa sistem çökmez; otomatik olarak `demo_fallback` moduna geçer ve loglara kaydeder.
2. **`SEMANTIC_MODE=demo` (Hızlı Geliştirme ve Test Modu):**
   * Hiçbir harici model ağırlığı indirilmez.
   * Deterministik word-hash embedding, kural tabanlı kümeleme ve sözcüksel reranker çalışır.
   * Unit testler 1.5 saniyede tamamlanır.

---

## 5. Ölçülen Çalışma Zamanı Gecikmeleri (Live Runtime Latencies)

Yerel NVIDIA GeForce RTX 3060 (12 GB VRAM) donanımında ölçülen canlı HTTP istek süreleri:

| Uç Nokta / Pipeline | İstek Metodu | Ortalama Yanıt Süresi | Bellek Tahsisi (GPU) |
| :--- | :--- | :---: | :---: |
| `GET /health` | Sağlık Kontrolü | 2.66 ms | — |
| `GET /api/system/status` | Model Durum & Telemetri | 7.92 ms | 2.19 GB |
| `GET /api/topics` | HDBSCAN Semantik Kümeleme | 326.08 ms (İlk Çalışma) | 2.19 GB |
| `GET /api/context/{topic_id}` | İki Aşamalı Bağlam Kartı | 110.82 ms | 2.19 GB |
| `GET /api/search?q=...` | E5 Doğal Dil Arama | 190.68 ms | 2.19 GB |
| `GET /api/recommendations` | Şeffaf Vektörlü Öneri Akışı | 150.88 ms | 2.19 GB |
| `POST /api/safety/analyze` | Sezgisel Moderasyon Risk Sinyali | 2.39 ms | — |

---

## 6. Sınırlar ve Şeffaflık Beyanları (Limitations & Disclosures)

1. **Canlı Platform API Eksikliği:** Mevcut sürüm bir TEKNOFEST 2026 yarışma prototipidir. Sistem canlı/resmi NSosyal API'sine bağlı değildir ve yetkisiz veri kazıma yapılmamaktadır. Veriler `data/demo_posts.json` içerisindeki sentetik Türkçe gönderilerden oluşmaktadır.
2. **Değerlendirme Veri Setinin Sınırları:** Faz 2A karşılaştırmasında kullanılan 50 dokümanlık erişim seti ve 40 metinlik kümeleme korpusu, Türkçe sosyal medya dinamiklerini simüle etmek üzere kurgulanmış kontrollü bir veri setidir; büyük ölçekli MTEB test setleri yerine geçmez, sistemi doğrulamaya yöneliktir.
3. **Reranker Skorunun Niteliği:** Reranker modelinin yüksek puan vermesi içeriğin anlamsal olarak soruya uygun olduğunu gösterir; içeriğin mutlak doğruluğunu veya resmiliğini teyit etmez.
