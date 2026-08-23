"use client";

import React, { useState } from "react";
import { api } from "../lib/api";
import { SafetyAnalysisResponse } from "../lib/types";
import {
  X,
  ShieldCheck,
  AlertTriangle,
  Send,
  Sparkles,
  Info,
  CheckCircle2,
  AlertCircle,
  FileCheck2,
} from "lucide-react";

interface SafetyAuditPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SafetyAuditPanel: React.FC<SafetyAuditPanelProps> = ({ isOpen, onClose }) => {
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SafetyAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.analyzeSafety(inputText);
      setResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError("Analiz başarısız: " + msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreset = (presetText: string) => {
    setInputText(presetText);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
      <div className="relative flex max-h-[92vh] w-full max-w-3xl flex-col rounded-2xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-5 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600/20 text-emerald-400 border border-emerald-500/30">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                İçerik Güvenlik Laboratuvarı
              </span>
              <h2 className="text-lg font-bold text-slate-100">
                Canlı Moderasyon & Risk Analizi (Faz 1 Sezgisel Motor)
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Preset Buttons */}
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Örnek Test Metinleri (Presets)
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() =>
                  handlePreset(
                    "Yapay zekâ ve açık kaynak yazılım projelerinin üniversitelerde desteklenmesi ülkemizin teknolojik bağımsızlığı açısından büyük önem taşıyor."
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-slate-700 hover:bg-slate-800 transition"
              >
                ✅ Normal Yapıcı Paylaşım
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "BEDAVA KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: http://bit.ly/bedava-hediye-2026 http://link-spam.xyz BEDAVA BEDAVA BEDAVA!!!"
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-slate-700 hover:bg-slate-800 transition"
              >
                ⚠️ Spam Bağlantı ve Büyük Harf
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "Bu yapılan tam bir sahtekar yaklaşımıdır, rezil ve ahmakça bir karar!"
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-slate-700 hover:bg-slate-800 transition"
              >
                🔍 Sert Dil / İnceleme İndikatörü
              </button>
            </div>
          </div>

          {/* Text Input Area */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300">
              Analiz Edilecek Paylaşım Metni:
            </label>
            <textarea
              rows={3}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Analiz etmek istediğiniz metni buraya yazın veya yukarıdaki hazır örneklerden birini seçin..."
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 p-3 text-xs text-slate-200 placeholder-slate-500 outline-none transition focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
            <div className="flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !inputText.trim()}
                className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-500 disabled:opacity-50 transition"
              >
                <Send className="h-3.5 w-3.5" />
                <span>{isLoading ? "Analiz Ediliyor..." : "Güvenlik Analizini Çalıştır"}</span>
              </button>
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-950/30 p-3 text-xs text-red-300">
              {error}
            </div>
          )}

          {/* Analysis Results Display */}
          {result && (
            <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-950/40 p-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <span className="text-xs text-slate-400">Genel Risk Seviyesi</span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span
                      className={`text-base font-bold ${
                        result.risk_vector.risk_level === "HIGH"
                          ? "text-red-400"
                          : result.risk_vector.risk_level === "MEDIUM"
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {result.risk_vector.risk_level === "HIGH"
                        ? "YÜKSEK RİSK (HIGH)"
                        : result.risk_vector.risk_level === "MEDIUM"
                        ? "ORTA RİSK (MEDIUM)"
                        : "DÜŞÜK RİSK / GÜVENLİ (LOW)"}
                    </span>
                    <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-xs text-slate-300">
                      Skor: {result.risk_vector.overall_risk_score}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] text-slate-400">İnsan Moderasyonu</span>
                  <div className="mt-0.5">
                    {result.risk_vector.human_review_recommended ? (
                      <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300 border border-amber-500/30 inline-flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        İnceleme Önerildi
                      </span>
                    ) : (
                      <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300 border border-emerald-500/30 inline-flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        Otomatik Onay
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Sub-scores Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Spam / Link Yoğunluğu</div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    {result.risk_vector.spam_score}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Tekrar / Şablon Benzerliği</div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    {result.risk_vector.repetition_score}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Koordineli Hesap Şüphesi</div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    {result.risk_vector.coordination_score}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Sert Dil / İndikatör</div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    {result.risk_vector.toxicity_score}
                  </div>
                </div>
              </div>

              {/* Triggered Signals List */}
              <div className="space-y-2 pt-2">
                <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <FileCheck2 className="h-4 w-4 text-blue-400" />
                  <span>Tetiklenen Güvenlik Sinyalleri ({result.risk_vector.signals.length})</span>
                </div>

                {result.risk_vector.signals.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">
                    Herhangi bir risk veya spam sinyali tetiklenmedi. Metin temiz görünüyor.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {result.risk_vector.signals.map((sig, sIdx) => (
                      <div
                        key={sIdx}
                        className="rounded-lg border border-slate-800 bg-slate-900 p-3 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="rounded bg-slate-800 px-1.5 py-0.2 font-mono text-[10px] text-blue-400">
                              {sig.rule_id}
                            </span>
                            <span className="font-semibold text-slate-200 uppercase text-[10px]">
                              {sig.category}
                            </span>
                          </div>
                          <span
                            className={`rounded px-1.5 py-0.2 text-[10px] font-semibold ${
                              sig.severity === "critical"
                                ? "bg-red-500/20 text-red-300"
                                : sig.severity === "warning"
                                ? "bg-amber-500/20 text-amber-300"
                                : "bg-blue-500/20 text-blue-300"
                            }`}
                          >
                            {sig.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-slate-300">{sig.description}</p>
                        {sig.detail && (
                          <div className="text-[11px] text-slate-400 italic pt-1">
                            Detay: {sig.detail}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Ethical Disclaimer */}
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-[11px] text-slate-400 flex items-start gap-2">
            <Info className="h-4 w-4 shrink-0 text-blue-400 mt-0.5" />
            <p>
              <strong>Etik Moderasyon Prensibi:</strong> Bu analiz motoru içerikleri kesin olarak
              &quot;nefret söylemi&quot; veya &quot;yasadışı&quot; olarak etiketlemez. Yalnızca insan
              moderatörlere ve kullanıcılara yardımcı olacak açıklanabilir risk göstergeleri ve
              şüphe puanları üretir.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-800 bg-slate-950/80 px-5 py-3 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1 text-amber-400/90">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Faz 1 Sezgisel Kural Analizörü</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg bg-slate-800 px-4 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};
