# NSosyal Pusula 🧭
### Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi
**TEKNOFEST 2026 Projesi**

[![Prototip Durumu](https://img.shields.io/badge/Prototip-Faz_1_Dikey_Kesit-blue.svg)](docs/architecture.md)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-green.svg)](LICENSE)
[![Veri Kaynağı](https://img.shields.io/badge/Veri_Kaynağı-Sentetik_Demo_Veri-orange.svg)](#veri-ve-entegrasyon-uyarısı)

---

## 📌 Proje Genel Bakışı (Project Overview)

**NSosyal Pusula**, modern sosyal medya platformlarında bilgi kirliliği, kutuplaşma, şeffaf olmayan algoritmalar ve bağlamından koparılmış içerik akışlarına karşı geliştirilmiş **yapay zekâ destekli bir sosyal medya zekâ ve şeffaflık katmanıdır**.

Platform, kullanıcılara salt kronolojik veya gizli öneri motorlarına dayalı bir akış sunmak yerine; paylaşımları anlamsal olarak kümeleyen, çoklu bakış açılarını sentezleyen **Bağlam Kartları (Context Cards)**, önerilerin gerekçelerini matematiksel ve metinsel olarak açıklayan **Şeffaf Öneri Sistemi (Transparent Recommendations)** ve zararlı/tekrar eden kalıpları insan denetimine uygun sinyallerle puanlayan **İçerik Güvenlik Katmanı (Content Safety & Moderation Signals)** sağlar.

---

## 🎯 Problem Tanımı ve Değer Önerisi (Problem Statement & Value Proposition)

| Mevcut Sosyal Medya Sorunları | NSosyal Pusula Çözümü |
| :--- | :--- |
| **Bağlam Eksikliği:** Olayların parçalı ve cımbızlanmış paylaşımlarla sunulması | **Bağlam Kartları (Context Cards):** Konunun özeti, zaman çizelgesi ve farklı görüşlerin sentezi |
| **Kara Kutu Algoritmalar:** Kullanıcının bir içeriği neden gördüğünü bilmemesi | **Şeffaf Öneri Motoru:** "Neden bunu görüyorum?" kartı ve açıklanabilir puanlama bileşenleri |
| **Yankı Odaları ve Kutuplaşma:** Tek taraflı içeriklerin beslenmesi | **Çeşitlilik & Denge Katsayısı:** Öneri fonksiyonunda çeşitlilik ve farklı perspektif teşviki |
| **Spam ve Koordineli Manipülasyon:** Bot ve bot-benzeri tekrarlı paylaşımlar | **Açıklanabilir Moderasyon Sinyalleri:** Kural tabanlı ve yapay zekâ destekli risk puanı |

---

## 🚀 Temel Yetenekler (Core Features)

### 1. Bağlam Kartları (Context Cards)
* **Anlamsal Kümeleme:** Aynı konu/olay hakkındaki paylaşımları otomatik olarak gruplar.
* **Çoklu Bakış Açısı Sentezi:** Konuya dair destekleyen, eleştiren ve nötr/kurumsal perspektifleri özetler.
* **Zaman Çizelgesi (Timeline):** Gelişmelerin kronolojik akışını çıkarır.
* **Kaynak ve Doğruluk Göstergeleri:** Tartışmada referans verilen kaynakların bağlamını sunar.

### 2. Şeffaf Öneri Sistemi (Transparent Recommendations)
* **"Neden Bunu Görüyorum?" Açıklaması:** Her önerilen içerik için kullanıcının ilgi alanı, konu yakınlığı, güncellik, çeşitlilik ve güvenlik faktörlerini şeffafça listeler.
* **Açıklanabilir Skorlama Modeli:**
  $$\text{Skor} = (w_1 \cdot \text{İlgi Benzerliği}) + (w_2 \cdot \text{Konu Yakınlığı}) + (w_3 \cdot \text{Güncellik}) + (w_4 \cdot \text{Çeşitlilik}) - (w_5 \cdot \text{Tekrar Cezası}) - (w_6 \cdot \text{Güvenlik Riski Cezası})$$

### 3. İçerik Güvenliği ve Moderasyon Sinyalleri (Content Safety)
* **Risk Skorlaması & Sinyaller:** Spam, metin tekrarı, şüpheli koordinasyon, toksik dil ve nefret söylemi potansiyelini skorlar.
* **İnsan Denetimine Uyumlu Tasarım:** Sistem içeriği doğrudan "kesin suçlu/zararlı" ilan etmez; moderatörler ve kullanıcılar için açıklayıcı risk sinyalleri ve güven skorları üretir.

---

## 🏗️ Mimari ve Katmanlar (Architecture Overview)

Sistem modüler ve gevşek bağlı (loosely coupled) bir monorepo olarak tasarlanmıştır:

```
NSOSYAL/
├── backend/                   # Python / FastAPI REST Servisi
│   ├── app/
│   │   ├── adapters/          # DataSourceAdapter (Demo JSON ve Gelecek API adaptörleri)
│   │   ├── api/               # REST API yönlendirmeleri (/health, /api/posts, /api/context, vb.)
│   │   ├── models/            # Pydantic veri modelleri ve şemalar
│   │   ├── services/          # Bağlam, güvenlik ve öneri motoru servisleri
│   │   └── config.py          # Yapılandırma yönetimi
│   └── requirements.txt
├── frontend/                  # Next.js / TypeScript / Tailwind CSS Kullanıcı Arayüzü
│   ├── src/
│   │   ├── app/               # Next.js App Router (Sayfalar ve düzenler)
│   │   ├── components/        # Feed, PostCard, ContextCardModal, ExplainModal, SafetyPanel
│   │   └── lib/               # API istemcisi ve TypeScript tip tanımları
│   └── package.json
├── data/                      # Sentetik / Mock Demo Veri Seti
│   └── demo_posts.json        # Test ve değerlendirme için üretilmiş Türkçe paylaşımlar
├── docs/                      # Detaylı Mimari ve Süreç Dokümantasyonu
│   └── architecture.md        # Pipeline akışları, veri yapıları ve adaptör spesifikasyonları
└── tests/                     # Backend birim ve entegrasyon testleri (Pytest)
```

Detaylı teknik mimari ve akış şemaları için: [docs/architecture.md](docs/architecture.md)

---

## 🛡️ Etik Yapay Zekâ ve Moderasyon İlkeleri (Ethical AI Principles)

1. **Açıklanabilirlik (Explainability):** Öneri ve risk sinyallerinin hiçbiri kara kutu kalmaz; kullanıcı ve denetçilere gerekçeleriyle sunulur.
2. **Kategorik Damgalamama:** Sistem içerikleri peşinen "kesin yalan/zararlı" olarak yaftalamaz, olasılık ve gösterge bazlı risk skoru üretir.
3. **Perspektif Çeşitliliği:** Algoritmalar yankı odası oluşumunu engellemek amacıyla çeşitlilik katsayısını ödüllendirir.
4. **Veri Gizliliği:** Kullanıcı profil modellemeleri minimal veri ve yerel tercihlerle yürütülecek şekilde planlanmıştır.

---

## ⚠️ Veri ve Entegrasyon Uyarısı (Important Notice on Data & API)

> **DİKKAT:** Bu proje bir TEKNOFEST 2026 yarışma prototipidir.
> * Mevcut aşamada sistem **herhangi bir canlı/resmi NSosyal API'sine bağlı değildir** ve yetkisiz veri kazıma (scraping) yapılmamaktadır.
> * Sistemde kullanılan paylaşımlar (`data/demo_posts.json`), prototipin yeteneklerini test etmek üzere kurgulanmış **tamamen sentetik ve jenerik Türkçe içeriklerdir**.
> * Backend'deki `DataSourceAdapter` arayüzü sayesinde, gelecekte resmi ve yetkilendirilmiş bir platform API'si entegre edildiğinde tek bir satır iş mantığı değişmeden adaptör değiştirilebilecektir.
> * Henüz büyük bir model fine-tune edilmemiş olup; Faz 1 aşamasında kural ve sezgisel (heuristic) motorlar çalışmaktadır.

---

## 🚦 Mevcut Prototip Durumu (Current Prototype Status - Phase 1)

* [x] Monorepo mimarisi ve standart dizin yapısı
* [x] Kapsamlı mimari tasarım ve dokümantasyon (`docs/architecture.md`)
* [x] Sentetik Türkçe sosyal medya test veri seti (`data/demo_posts.json`)
* [x] `DataSourceAdapter` soyutlaması ve JSON dosya adaptörü
* [x] FastAPI tabanlı REST API (`/health`, `/api/posts`, `/api/topics`, `/api/context/{topic_id}`, `/api/safety/analyze`, `/api/recommendations`)
* [x] Açıklanabilir Sezgisel Güvenlik ve Spam Analiz Motoru
* [x] Açıklanabilir Şeffaf Öneri Skorlama Servisi
* [x] Next.js 14/15, TypeScript ve Tailwind CSS modern Web Arayüzü
* [x] Bağlam Kartı Modalı, "Neden Bunu Görüyorum?" Skoru Modalı ve Canlı Güvenlik Denetim Paneli
* [x] Pytest birim ve iş mantığı testleri

---

## 🛠️ Yerel Geliştirme Kurulumu (Local Development Setup)

### Gereksinimler
* Python 3.10+
* Node.js 18+ & npm / pnpm

### 1. Depoyu Klonlayın ve Yapılandırın
```bash
git clone <repository-url>
cd NSOSYAL
cp .env.example .env
```

### 2. Backend Kurulumu ve Çalıştırma
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
Backend API dökümantasyonu: `http://localhost:8000/docs`

### 3. Frontend Kurulumu ve Çalıştırma
Yeni bir terminalde:
```bash
cd frontend
npm install
npm run dev
```
Web Arayüzü: `http://localhost:3000`

### 4. Testleri Çalıştırma
```bash
cd backend
pytest ../tests -v
```

---

## 🔮 Gelecek Yol Haritası (Planned AI Components - Next Phases)

1. **Türkçe Cümle Gömme Modelleri (Embeddings):** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` veya yerli Türkçe açık kaynak BERT modellerinin entegrasyonu.
2. **Dinamik Konu Keşfi (BERTopic / HDBSCAN):** Paylaşımlardan dinamik olay ve konu kümeleme.
3. **Açık Kaynak LLM ile Bağlam Sentezi:** Ollama / vLLM veya bulut LLM sağlayıcıları üzerinden otomatik çoklu perspektif sentezleme.
4. **Toksisite ve Ayrımcılık Sınıflandırıcısı:** Türkçe moderasyon veri setleriyle eğitilmiş hafif sınıflandırıcılar.
5. **Graf Tabanlı Koordinasyon Analizi:** Şüpheli bot ağlarını tespit etmek için kullanıcı etkileşim grafı analizi.
