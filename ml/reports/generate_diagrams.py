"""Generate professional SVG and PNG diagrams for TEKNOFEST Technical Report."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "report_assets", "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)


def create_system_architecture_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 850" width="100%" height="100%" style="background-color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="grad-core" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="grad-blue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB"/>
      <stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <linearGradient id="grad-emerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#047857"/>
    </linearGradient>
    <linearGradient id="grad-purple" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#6D28D9"/>
    </linearGradient>
    <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#D97706"/>
      <stop offset="100%" stop-color="#B45309"/>
    </linearGradient>
    <linearGradient id="grad-rose" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E11D48"/>
      <stop offset="100%" stop-color="#BE123C"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#94A3B8"/>
    </marker>
    <marker id="arrow-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#A855F7"/>
    </marker>
  </defs>

  <!-- Title & Header -->
  <text x="600" y="45" text-anchor="middle" fill="#F8FAFC" font-size="22" font-weight="800" letter-spacing="0.5">NSOSYAL PUSULA — SİSTEM MİMARİSİ</text>
  <text x="600" y="70" text-anchor="middle" fill="#94A3B8" font-size="13" font-weight="500">Kanıta Dayalı Türkçe Anlamsal Analiz, Şeffaf Moderasyon ve Açıklanabilir Öneri Hattı</text>

  <!-- Container Box 1: Data Ingestion & Preprocessing -->
  <g transform="translate(40, 100)" filter="url(#shadow)">
    <rect width="240" height="700" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <rect width="240" height="38" rx="16" fill="#0F172A"/>
    <rect y="22" width="240" height="16" fill="#0F172A"/>
    <text x="120" y="24" text-anchor="middle" fill="#38BDF8" font-size="13" font-weight="700">1. VERİ KATMANI</text>

    <!-- Post Adapter Node -->
    <g transform="translate(15, 60)">
      <rect width="210" height="85" rx="10" fill="#0F172A" stroke="#475569" stroke-width="1"/>
      <text x="105" y="26" text-anchor="middle" fill="#F1F5F9" font-size="12" font-weight="700">DataSourceAdapter</text>
      <text x="105" y="48" text-anchor="middle" fill="#94A3B8" font-size="10">Sentetik &amp; Canlı NSosyal Akışı</text>
      <text x="105" y="65" text-anchor="middle" fill="#64748B" font-size="9.5">demo_posts.json (70 Örnek)</text>
    </g>

    <!-- Preprocessing Node -->
    <g transform="translate(15, 175)">
      <rect width="210" height="85" rx="10" fill="#0F172A" stroke="#475569" stroke-width="1"/>
      <text x="105" y="26" text-anchor="middle" fill="#F1F5F9" font-size="12" font-weight="700">Ön İşleme &amp; Temizleme</text>
      <text x="105" y="48" text-anchor="middle" fill="#94A3B8" font-size="10">URL &amp; Karakter Normalizasyonu</text>
      <text x="105" y="65" text-anchor="middle" fill="#64748B" font-size="9.5">topic_hint İzolasyonu (Gizli Test)</text>
    </g>

    <!-- Ingestion Pipeline Arrow -->
    <path d="M 120 145 L 120 170" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>
    <path d="M 120 260 L 120 300" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Dual Router Node -->
    <g transform="translate(15, 305)">
      <rect width="210" height="120" rx="10" fill="#0F172A" stroke="#0284C7" stroke-width="1.5"/>
      <text x="105" y="26" text-anchor="middle" fill="#38BDF8" font-size="12" font-weight="700">Vektör Dağıtıcı (Router)</text>
      <text x="105" y="50" text-anchor="middle" fill="#E2E8F0" font-size="10.5">• Kümeleme &amp; Bağlam Hattı</text>
      <text x="105" y="70" text-anchor="middle" fill="#E2E8F0" font-size="10.5">• Doğal Dil Arama Hattı</text>
      <text x="105" y="90" text-anchor="middle" fill="#E2E8F0" font-size="10.5">• Güvenlik &amp; Moderasyon Hattı</text>
    </g>

    <!-- Hardware Box -->
    <g transform="translate(15, 460)">
      <rect width="210" height="210" rx="10" fill="#090D16" stroke="#334155" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#A855F7" font-size="11" font-weight="700">DONANIM PROFİLİ</text>
      <text x="15" y="50" fill="#CBD5E1" font-size="10">• GPU: RTX 3060 (12 GB)</text>
      <text x="15" y="72" fill="#CBD5E1" font-size="10">• CPU: i5-13600KF (14C/20T)</text>
      <text x="15" y="94" fill="#CBD5E1" font-size="10">• RAM: 32 GB DDR5</text>
      <text x="15" y="116" fill="#CBD5E1" font-size="10">• CUDA: v12.4 | PyTorch 2.6</text>
      <text x="15" y="138" fill="#CBD5E1" font-size="10">• Model VRAM: 2.28 GB</text>
      <text x="15" y="160" fill="#CBD5E1" font-size="10">• Backend: FastAPI</text>
      <text x="15" y="182" fill="#CBD5E1" font-size="10">• Frontend: Next.js 14</text>
    </g>
  </g>

  <!-- Connecting Arrows from Router to 3 Main Pillars -->
  <path d="M 280 345 C 310 345, 310 200, 340 200" fill="none" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 280 365 C 310 365, 310 460, 340 460" fill="none" stroke="#A855F7" stroke-width="2" marker-end="url(#arrow-purple)"/>
  <path d="M 280 385 C 310 385, 310 700, 340 700" fill="none" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-emerald)"/>

  <!-- Container Box 2: Semantic Pipeline & Context Cards (Top Branch) -->
  <g transform="translate(340, 100)" filter="url(#shadow)">
    <rect width="520" height="230" rx="16" fill="#1E293B" stroke="#0284C7" stroke-width="1.5"/>
    <rect width="520" height="32" rx="16" fill="#0369A1"/>
    <rect y="16" width="520" height="16" fill="#0369A1"/>
    <text x="260" y="22" text-anchor="middle" fill="#FFFFFF" font-size="12" font-weight="700">2. ANLAMSAL KÜMELEME &amp; BAĞLAM KARTI HATTI (ModernBERT-TR)</text>

    <!-- ModernBERT-TR-Embed -->
    <g transform="translate(20, 50)">
      <rect width="140" height="75" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="70" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">ModernBERT-TR</text>
      <text x="70" y="42" text-anchor="middle" fill="#F1F5F9" font-size="10">Yoğun Gömme (768d)</text>
      <text x="70" y="60" text-anchor="middle" fill="#94A3B8" font-size="9">149M • L2 Normalize</text>
    </g>

    <!-- Arrow -->
    <path d="M 160 87 L 180 87" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- HDBSCAN -->
    <g transform="translate(185, 50)">
      <rect width="140" height="75" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="70" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">HDBSCAN</text>
      <text x="70" y="42" text-anchor="middle" fill="#F1F5F9" font-size="10">Yoğunluk Kümeleme</text>
      <text x="70" y="60" text-anchor="middle" fill="#94A3B8" font-size="9">NMI: 0.8086 • ARI: 0.659</text>
    </g>

    <!-- Arrow -->
    <path d="M 325 87 L 345 87" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- c-TF-IDF Titling & Perspectives -->
    <g transform="translate(350, 50)">
      <rect width="150" height="75" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="75" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">Dinamik c-TF-IDF</text>
      <text x="75" y="42" text-anchor="middle" fill="#F1F5F9" font-size="10">Ayırt Edici N-Gram</text>
      <text x="75" y="60" text-anchor="middle" fill="#94A3B8" font-size="9">Konu Başlığı &amp; Perspektif</text>
    </g>

    <!-- Context Source Dense Retrieval & Reranker Sub-box -->
    <g transform="translate(20, 140)">
      <rect width="480" height="75" rx="8" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="15" y="22" fill="#38BDF8" font-size="10.5" font-weight="700">Bağlam Kaynağı Getirme &amp; Cross-Encoder Reranker (nDCG@10: 0.9873):</text>
      <text x="15" y="44" fill="#CBD5E1" font-size="9.5">• 1. Aşama: ModernBERT Dense Retrieval (Top-15 Aday)</text>
      <text x="15" y="62" fill="#CBD5E1" font-size="9.5">• 2. Aşama: Moderasyon Filtreleme → ModernBERT-TR-Reranker (Top-5 Güvenilir Kaynak)</text>
    </g>
  </g>

  <!-- Container Box 3: Moderation & Coordination Risk (Middle Branch) -->
  <g transform="translate(340, 350)" filter="url(#shadow)">
    <rect width="520" height="230" rx="16" fill="#1E293B" stroke="#7C3AED" stroke-width="1.5"/>
    <rect width="520" height="32" rx="16" fill="#6D28D9"/>
    <rect y="16" width="520" height="16" fill="#6D28D9"/>
    <text x="260" y="22" text-anchor="middle" fill="#FFFFFF" font-size="12" font-weight="700">3. ŞEFFAF MODERASYON &amp; KOORDİNASYON RİSKİ KATMANI</text>

    <!-- 4 Multi-dimensional Detectors -->
    <g transform="translate(15, 48)">
      <rect width="115" height="75" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="57" y="20" text-anchor="middle" fill="#C084FC" font-size="10" font-weight="700">ModernBERT</text>
      <text x="57" y="34" text-anchor="middle" fill="#C084FC" font-size="9.5">Guardrail</text>
      <text x="57" y="52" text-anchor="middle" fill="#94A3B8" font-size="8.5">11 Tehlike Sınıfı</text>
      <text x="57" y="66" text-anchor="middle" fill="#94A3B8" font-size="8.5">F1: 0.9377 (TEST)</text>
    </g>

    <g transform="translate(140, 48)">
      <rect width="115" height="75" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="57" y="22" text-anchor="middle" fill="#C084FC" font-size="10" font-weight="700">Spam Dedektörü</text>
      <text x="57" y="44" text-anchor="middle" fill="#94A3B8" font-size="8.5">Şüpheli TLD</text>
      <text x="57" y="58" text-anchor="middle" fill="#94A3B8" font-size="8.5">Link Yoğunluğu</text>
      <text x="57" y="69" text-anchor="middle" fill="#94A3B8" font-size="8">Büyük Harf Oranı</text>
    </g>

    <g transform="translate(265, 48)">
      <rect width="115" height="75" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="57" y="22" text-anchor="middle" fill="#C084FC" font-size="10" font-weight="700">Tekrar Dedektörü</text>
      <text x="57" y="44" text-anchor="middle" fill="#94A3B8" font-size="8.5">Metin-İçi Tekrar</text>
      <text x="57" y="58" text-anchor="middle" fill="#94A3B8" font-size="8.5">Külliyat N-Gram</text>
      <text x="57" y="69" text-anchor="middle" fill="#94A3B8" font-size="8">Kopya Eşleşmesi</text>
    </g>

    <g transform="translate(390, 48)">
      <rect width="115" height="75" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="57" y="22" text-anchor="middle" fill="#C084FC" font-size="10" font-weight="700">Koordinasyon</text>
      <text x="57" y="44" text-anchor="middle" fill="#94A3B8" font-size="8.5">Şablon Benzerliği</text>
      <text x="57" y="58" text-anchor="middle" fill="#94A3B8" font-size="8.5">Zaman Pencereleri</text>
      <text x="57" y="69" text-anchor="middle" fill="#94A3B8" font-size="8">Çoklu Hesap Ağı</text>
    </g>

    <!-- Moderation Fusion Sub-box -->
    <g transform="translate(15, 135)">
      <rect width="490" height="80" rx="8" fill="#0F172A" stroke="#7C3AED" stroke-width="1"/>
      <text x="15" y="22" fill="#C084FC" font-size="10.5" font-weight="700">Moderasyon Füzyon Servisi (ModerationFusionService):</text>
      <text x="15" y="42" fill="#E2E8F0" font-size="9.5">• Çok Boyutlu Risk Vektörü (Bileşik Risk Skoru: 0.0 - 1.0)</text>
      <text x="15" y="58" fill="#E2E8F0" font-size="9.5">• İnceleme Önceliği: [LOW | MEDIUM | HIGH | CRITICAL]</text>
      <text x="15" y="74" fill="#E2E8F0" font-size="9.5">• İnsan Moderatör İnceleme Önerisi &amp; Açıklanabilir Gerekçe</text>
    </g>
  </g>

  <!-- Container Box 4: Recommendation Engine & Semantic Search (Bottom Branch) -->
  <g transform="translate(340, 600)" filter="url(#shadow)">
    <rect width="520" height="200" rx="16" fill="#1E293B" stroke="#059669" stroke-width="1.5"/>
    <rect width="520" height="32" rx="16" fill="#047857"/>
    <rect y="16" width="520" height="16" fill="#047857"/>
    <text x="260" y="22" text-anchor="middle" fill="#FFFFFF" font-size="12" font-weight="700">4. AÇIKLANABİLİR ÖNERİ MOTORU &amp; DOĞAL DİL ARAMA</text>

    <!-- Multilingual-E5 Search Sub-box -->
    <g transform="translate(20, 48)">
      <rect width="230" height="65" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="115" y="22" text-anchor="middle" fill="#34D399" font-size="10.5" font-weight="700">Multilingual-E5-Large-Instruct</text>
      <text x="115" y="40" text-anchor="middle" fill="#F1F5F9" font-size="9.5">Serbest Metin Semantik Arama</text>
      <text x="115" y="55" text-anchor="middle" fill="#94A3B8" font-size="8.5">560M • Cosine Similarity</text>
    </g>

    <!-- Explainable Recommendation Sub-box -->
    <g transform="translate(265, 48)">
      <rect width="235" height="65" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="117" y="22" text-anchor="middle" fill="#34D399" font-size="10.5" font-weight="700">Açıklanabilir Öneri Formülü</text>
      <text x="117" y="40" text-anchor="middle" fill="#F1F5F9" font-size="9">İlgi + Konu + Güncellik + Çeşitlilik</text>
      <text x="117" y="55" text-anchor="middle" fill="#F43F5E" font-size="8.5">- Spam Cezası - Tekrar Cezası</text>
    </g>

    <!-- Grounded Explanation Banner -->
    <g transform="translate(20, 125)">
      <rect width="480" height="60" rx="8" fill="#0F172A" stroke="#059669" stroke-width="1"/>
      <text x="240" y="24" text-anchor="middle" fill="#34D399" font-size="10.5" font-weight="700">Şeffaf Karar Dökümü ("Neden bunu görüyorum?")</text>
      <text x="240" y="45" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Her önerilen gönderi için izlenebilir 6 puanlama faktörü ve gerekçe metni</text>
    </g>
  </g>

  <!-- Connecting to UI Presentation Layer -->
  <path d="M 860 215 C 890 215, 890 400, 920 400" fill="none" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 860 465 C 890 465, 890 440, 920 440" fill="none" stroke="#A855F7" stroke-width="2" marker-end="url(#arrow-purple)"/>
  <path d="M 860 700 C 890 700, 890 480, 920 480" fill="none" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-emerald)"/>

  <!-- Container Box 5: Frontend UI Presentation Layer (Right) -->
  <g transform="translate(920, 100)" filter="url(#shadow)">
    <rect width="240" height="700" rx="16" fill="#1E293B" stroke="#F59E0B" stroke-width="1.5"/>
    <rect width="240" height="38" rx="16" fill="#78350F"/>
    <rect y="22" width="240" height="16" fill="#78350F"/>
    <text x="120" y="24" text-anchor="middle" fill="#FDE68A" font-size="12" font-weight="700">5. KULLANICI ARAYÜZÜ (Next.js 14)</text>

    <!-- Context Card Component -->
    <g transform="translate(15, 55)">
      <rect width="210" height="100" rx="10" fill="#0F172A" stroke="#F59E0B" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#FBBF24" font-size="11" font-weight="700">Bağlam Kartı Modülü</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9.5">• Dinamik Konu Özeti</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9.5">• Çoklu Perspektif Sekmeleri</text>
      <text x="15" y="82" fill="#CBD5E1" font-size="9.5">• Yeniden Sıralı Kaynaklar</text>
    </g>

    <!-- Transparent Recommendation Component -->
    <g transform="translate(15, 175)">
      <rect width="210" height="100" rx="10" fill="#0F172A" stroke="#F59E0B" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#FBBF24" font-size="11" font-weight="700">Neden Görüyorum? Modalı</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9.5">• 6 Faktörlü Etki Grafiği</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9.5">• Ham Puan ve Ağırlıklar</text>
      <text x="15" y="82" fill="#CBD5E1" font-size="9.5">• Kullanıcı Geri Bildirim Butonu</text>
    </g>

    <!-- Safety Audit Panel Component -->
    <g transform="translate(15, 295)">
      <rect width="210" height="100" rx="10" fill="#0F172A" stroke="#F59E0B" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#FBBF24" font-size="11" font-weight="700">Moderasyon Laboratuvarı</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9.5">• 11 Tehlike İlerleme Çubuğu</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9.5">• Öncelik Rozetleri (CRITICAL..)</text>
      <text x="15" y="82" fill="#CBD5E1" font-size="9.5">• Koordinasyon &amp; Spam Kanıtı</text>
    </g>

    <!-- Natural Language Search Bar Component -->
    <g transform="translate(15, 415)">
      <rect width="210" height="90" rx="10" fill="#0F172A" stroke="#F59E0B" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#FBBF24" font-size="11" font-weight="700">Doğal Dil Arama Barı</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9.5">• Anlamsal Vektör Araması</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9.5">• Gecikme Göstergesi (ms)</text>
      <text x="15" y="80" fill="#CBD5E1" font-size="9.5">• Canlı Filtreleme</text>
    </g>

    <!-- System Status Badge -->
    <g transform="translate(15, 525)">
      <rect width="210" height="145" rx="10" fill="#090D16" stroke="#475569" stroke-width="1"/>
      <text x="105" y="24" text-anchor="middle" fill="#10B981" font-size="11" font-weight="700">CANLI SİSTEM DURUMU</text>
      <text x="15" y="48" fill="#94A3B8" font-size="9.5">Mod: Gerçek ML (CUDA)</text>
      <text x="15" y="68" fill="#94A3B8" font-size="9.5">Gömme: ModernBERT-TR</text>
      <text x="15" y="88" fill="#94A3B8" font-size="9.5">Reranker: ModernBERT-TR</text>
      <text x="15" y="108" fill="#94A3B8" font-size="9.5">Guardrail: ModernBERT-TR</text>
      <text x="15" y="128" fill="#94A3B8" font-size="9.5">Arama: mE5-Large-Instruct</text>
    </g>
  </g>
</svg>"""

    svg_path = os.path.join(DIAGRAMS_DIR, "system_architecture_diagram.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated Architecture SVG: {svg_path}")


def create_user_flows_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 720" width="100%" height="100%" style="background-color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="grad-blue-card" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <filter id="flow-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
    <marker id="flow-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38BDF8"/>
    </marker>
    <marker id="flow-arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981"/>
    </marker>
    <marker id="flow-arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#A855F7"/>
    </marker>
  </defs>

  <!-- Main Title -->
  <text x="575" y="40" text-anchor="middle" fill="#F8FAFC" font-size="20" font-weight="800">NSOSYAL PUSULA — KULLANICI AKIŞ DİYAGRAMI</text>
  <text x="575" y="62" text-anchor="middle" fill="#94A3B8" font-size="12">3 Temel Kullanıcı Deneyimi Döngüsü: Bağlam Keşfi, Şeffaf Öneri ve Moderasyon Denetimi</text>

  <!-- FLOW A: CONTEXT DISCOVERY -->
  <g transform="translate(40, 90)" filter="url(#flow-shadow)">
    <rect width="1070" height="170" rx="14" fill="#1E293B" stroke="#0284C7" stroke-width="1.5"/>
    <rect width="1070" height="28" rx="14" fill="#0369A1"/>
    <rect y="14" width="1070" height="14" fill="#0369A1"/>
    <text x="20" y="19" fill="#FFFFFF" font-size="11.5" font-weight="700">AKIŞ A: BAĞLAM VE PERSPEKTİF KEŞFİ (Context Discovery Flow)</text>

    <!-- Step A1 -->
    <g transform="translate(25, 45)">
      <rect width="160" height="100" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="80" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">1. Akışta Gezinme</text>
      <text x="80" y="48" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Kullanıcı akışta</text>
      <text x="80" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">bir gönderi görür</text>
      <text x="80" y="85" text-anchor="middle" fill="#FBBF24" font-size="9" font-weight="600">"Bağlamı Gör" Butonu</text>
    </g>

    <path d="M 190 95 L 225 95" stroke="#38BDF8" stroke-width="2" marker-end="url(#flow-arrow)"/>

    <!-- Step A2 -->
    <g transform="translate(235, 45)">
      <rect width="175" height="100" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="87" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">2. Anlamsal Küme</text>
      <text x="87" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">ModernBERT + HDBSCAN</text>
      <text x="87" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Gönderinin ait olduğu</text>
      <text x="87" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">anlamsal küme yüklenir</text>
    </g>

    <path d="M 415 95 L 450 95" stroke="#38BDF8" stroke-width="2" marker-end="url(#flow-arrow)"/>

    <!-- Step A3 -->
    <g transform="translate(460, 45)">
      <rect width="180" height="100" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="90" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">3. Bağlam Kartı Açılır</text>
      <text x="90" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Dinamik c-TF-IDF Başlık</text>
      <text x="90" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Tartışma Özeti &amp;</text>
      <text x="90" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Küme Üyelik Skoru</text>
    </g>

    <path d="M 645 95 L 680 95" stroke="#38BDF8" stroke-width="2" marker-end="url(#flow-arrow)"/>

    <!-- Step A4 -->
    <g transform="translate(690, 45)">
      <rect width="170" height="100" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="85" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">4. Perspektif Ayrıştırma</text>
      <text x="85" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Lehte / Aleyhte / Nötr</text>
      <text x="85" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Sekmeler arası geçiş &amp;</text>
      <text x="85" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Temsilci kanıt alıntıları</text>
    </g>

    <path d="M 865 95 L 900 95" stroke="#38BDF8" stroke-width="2" marker-end="url(#flow-arrow)"/>

    <!-- Step A5 -->
    <g transform="translate(910, 45)">
      <rect width="145" height="100" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
      <text x="72" y="24" text-anchor="middle" fill="#38BDF8" font-size="11" font-weight="700">5. Bağlam Kaynakları</text>
      <text x="72" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Reranker sıralı</text>
      <text x="72" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">bağlam kaynakları</text>
      <text x="72" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">&amp; referans bağlantı</text>
    </g>
  </g>

  <!-- FLOW B: TRANSPARENT RECOMMENDATION -->
  <g transform="translate(40, 290)" filter="url(#flow-shadow)">
    <rect width="1070" height="170" rx="14" fill="#1E293B" stroke="#059669" stroke-width="1.5"/>
    <rect width="1070" height="28" rx="14" fill="#047857"/>
    <rect y="14" width="1070" height="14" fill="#047857"/>
    <text x="20" y="19" fill="#FFFFFF" font-size="11.5" font-weight="700">AKIŞ B: ŞEFFAF VE AÇIKLANABİLİR ÖNERİ (Explainable Recommendation Flow)</text>

    <!-- Step B1 -->
    <g transform="translate(25, 45)">
      <rect width="165" height="100" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="82" y="24" text-anchor="middle" fill="#34D399" font-size="11" font-weight="700">1. Kişiselleştirilmiş Akış</text>
      <text x="82" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Kullanıcı ilgi profiliyle</text>
      <text x="82" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">eşleşen gönderi sunulur</text>
      <text x="82" y="85" text-anchor="middle" fill="#34D399" font-size="9" font-weight="600">Rozet: "%75 İlgi Uyumu"</text>
    </g>

    <path d="M 195 95 L 235 95" stroke="#10B981" stroke-width="2" marker-end="url(#flow-arrow-green)"/>

    <!-- Step B2 -->
    <g transform="translate(245, 45)">
      <rect width="180" height="100" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="90" y="24" text-anchor="middle" fill="#34D399" font-size="11" font-weight="700">2. Neden Bunu Görüyorum?</text>
      <text x="90" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Kullanıcı gönderi kartındaki</text>
      <text x="90" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">şeffaflık butonuna</text>
      <text x="90" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">tıklar</text>
    </g>

    <path d="M 430 95 L 470 95" stroke="#10B981" stroke-width="2" marker-end="url(#flow-arrow-green)"/>

    <!-- Step B3 -->
    <g transform="translate(480, 45)">
      <rect width="260" height="100" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="130" y="24" text-anchor="middle" fill="#34D399" font-size="11" font-weight="700">3. 6 Faktörlü Skor Ayrışımı</text>
      <text x="15" y="48" fill="#CBD5E1" font-size="9">• Anlamsal İlgi: +22.6 pt | Konu: +21.2 pt</text>
      <text x="15" y="66" fill="#CBD5E1" font-size="9">• Güncellik: +20.0 pt | Çeşitlilik: +11.2 pt</text>
      <text x="15" y="84" fill="#CBD5E1" font-size="9">• Spam / Tekrar Cezaları: -0.0 pt</text>
    </g>

    <path d="M 745 95 L 785 95" stroke="#10B981" stroke-width="2" marker-end="url(#flow-arrow-green)"/>

    <!-- Step B4 -->
    <g transform="translate(795, 45)">
      <rect width="255" height="100" rx="8" fill="#0F172A" stroke="#10B981" stroke-width="1"/>
      <text x="127" y="24" text-anchor="middle" fill="#34D399" font-size="11" font-weight="700">4. Kullanıcı Denetimi</text>
      <text x="127" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Açıklanabilir gerekçe metni</text>
      <text x="127" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Geri bildirim butonları:</text>
      <text x="127" y="85" text-anchor="middle" fill="#FBBF24" font-size="9" font-weight="600">[Daha Çok Gör] | [Daha Az Gör]</text>
    </g>
  </g>

  <!-- FLOW C: MODERATION & RISK AUDIT -->
  <g transform="translate(40, 490)" filter="url(#flow-shadow)">
    <rect width="1070" height="170" rx="14" fill="#1E293B" stroke="#7C3AED" stroke-width="1.5"/>
    <rect width="1070" height="28" rx="14" fill="#6D28D9"/>
    <rect y="14" width="1070" height="14" fill="#6D28D9"/>
    <text x="20" y="19" fill="#FFFFFF" font-size="11.5" font-weight="700">AKIŞ C: ŞEFFAF İÇERİK GÜVENLİĞİ VE MODERASYON DENETİMİ (Moderation &amp; Risk Audit Flow)</text>

    <!-- Step C1 -->
    <g transform="translate(25, 45)">
      <rect width="165" height="100" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="82" y="24" text-anchor="middle" fill="#C084FC" font-size="11" font-weight="700">1. Metin Girişi</text>
      <text x="82" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Kullanıcı veya denetçi</text>
      <text x="82" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">metni gönderir ya da</text>
      <text x="82" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">hazır senaryo seçer</text>
    </g>

    <path d="M 195 95 L 235 95" stroke="#A855F7" stroke-width="2" marker-end="url(#flow-arrow-purple)"/>

    <!-- Step C2 -->
    <g transform="translate(245, 45)">
      <rect width="190" height="100" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="95" y="24" text-anchor="middle" fill="#C084FC" font-size="11" font-weight="700">2. Çok Boyutlu Analiz</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9">• ModernBERT Guardrail (11 Sınıf)</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9">• Spam / TLD / Link Yoğunluğu</text>
      <text x="15" y="82" fill="#CBD5E1" font-size="9">• Koordinasyon &amp; Kopya Şablon</text>
    </g>

    <path d="M 440 95 L 475 95" stroke="#A855F7" stroke-width="2" marker-end="url(#flow-arrow-purple)"/>

    <!-- Step C3 -->
    <g transform="translate(485, 45)">
      <rect width="230" height="100" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="115" y="24" text-anchor="middle" fill="#C084FC" font-size="11" font-weight="700">3. Eşik Karşılaştırma &amp; Füzyon</text>
      <text x="115" y="46" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Kalibre Edilmiş Eşikler (DEV)</text>
      <text x="115" y="64" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Bileşik Risk Skoru Hesaplanır</text>
      <text x="115" y="82" text-anchor="middle" fill="#CBD5E1" font-size="9.5">Öncelik: LOW / MED / HIGH / CRIT</text>
    </g>

    <path d="M 720 95 L 755 95" stroke="#A855F7" stroke-width="2" marker-end="url(#flow-arrow-purple)"/>

    <!-- Step C4 -->
    <g transform="translate(765, 45)">
      <rect width="285" height="100" rx="8" fill="#0F172A" stroke="#A855F7" stroke-width="1"/>
      <text x="142" y="24" text-anchor="middle" fill="#C084FC" font-size="11" font-weight="700">4. Şeffaf Çıktı &amp; İnceleme Kararı</text>
      <text x="15" y="46" fill="#CBD5E1" font-size="9">• İnsan Moderatör İnceleme Önerisi</text>
      <text x="15" y="64" fill="#CBD5E1" font-size="9">• Gerekçeli Türkçe Risk Açıklaması</text>
      <text x="15" y="82" fill="#CBD5E1" font-size="9">• Asla otomatik kesin sansür uygulanmaz</text>
    </g>
  </g>
</svg>"""

    svg_path = os.path.join(DIAGRAMS_DIR, "user_flows_diagram.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated User Flows SVG: {svg_path}")


if __name__ == "__main__":
    create_system_architecture_svg()
    create_user_flows_svg()
    print("Diagrams generated successfully!")
