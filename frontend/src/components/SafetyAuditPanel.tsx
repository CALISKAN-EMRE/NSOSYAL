"use client";

import React, { useState } from "react";
import { api } from "../lib/api";
import { SafetyAnalysisResponse } from "../lib/types";
import {
  X,
  ShieldCheck,
  Send,
  Sparkles,
  Info,
  CheckCircle2,
  AlertCircle,
  FileCheck2,
  Activity,
  Users,
  Copy,
  Link as LinkIcon,
  Flame,
} from "lucide-react";

interface SafetyAuditPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const CATEGORY_NAMES_TR: Record<string, string> = {
  unsafe: "Genel Güvensizlik",
  VIOLENT_CRIMES: "Şiddet Eylemi / Tehdit",
  NON_VIOLENT_CRIMES: "Yasadışı / Finansal Suç",
  HATE_DISCRIMINATION: "Ayrımcılık / Nefret Söylemi",
  HARASSMENT_OFFENSIVE: "Taciz / Ağır Hakaret",
  SEXUAL_CONTENT_ADULT: "Müstehcen / Yetişkin İçerik",
  CSAE: "Çocuk İstismarı (CSAE)",
  SELF_HARM_SUICIDE: "Kendine Zarar Verme / İntihar",
  INJECTION_JAILBREAK: "Sistem / Komut Enjeksiyonu",
  MISINFORMATION_POLITICAL: "Siyasi Manipülasyon",
  PRIVACY_VIOLATION: "Kişisel Veri / Gizlilik İhlali",
};

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
      <div className="relative flex max-h-[92vh] w-full max-w-4xl flex-col rounded-2xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-5 bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  Moderasyon & Koordinasyon Laboratuvarı
                </span>
                <span className="rounded bg-indigo-950 px-2 py-0.5 text-[10px] font-mono text-indigo-300 border border-indigo-800/40">
                  Faz 2C (ModernBERT-TR Guardrail)
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-100">
                Çok Boyutlu İçerik Güvenliği ve Şeffaf Moderasyon Analizi
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
              Hazır Test Senaryoları (Presets)
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() =>
                  handlePreset(
                    "Eğitimde yapay zekâ uygulamaları üzerine hazırlanan yeni müfredat rehberini inceledim, öğretmen eğitimi için çok faydalı adımlar var."
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-emerald-500 hover:bg-slate-800 transition"
              >
                ✅ Normal/Yapıcı Paylaşım
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "Sen tam bir sahtekar ve rezil bir yalancısın, insanları kandırmaktan utanmıyor musun aşağılık herif!"
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-amber-500 hover:bg-slate-800 transition"
              >
                ⚠️ Taciz & Ağır Hakaret
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "Belli bir etnik kökene sahip insanlardan nefret ediyorum, bu ülkedeki tüm bu ırk mensupları zorla sürülmeli."
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-red-500 hover:bg-slate-800 transition"
              >
                🚨 Ayrımcılık / Nefret Riski
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "İNANILMAZ KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: http://bit.ly/bedava-2026 http://link-spam.xyz BEDAVA BEDAVA BEDAVA!!!"
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-amber-500 hover:bg-slate-800 transition"
              >
                🔗 Spam Bağlantı & Büyük Harf
              </button>
              <button
                onClick={() =>
                  handlePreset(
                    "Ücretsiz hediye çeki kazanmak için hemen tıklayın ve formu doldurun link profilde http://hediye-sahte.com"
                  )
                }
                className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 hover:border-purple-500 hover:bg-slate-800 transition"
              >
                🤖 Koordineli Şablon Metin
              </button>
            </div>
          </div>

          {/* Text Input Area */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300">
              Analiz Edilecek Türkçe Paylaşım Metni:
            </label>
            <textarea
              rows={3}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Analiz etmek istediğiniz metni buraya yazın veya yukarıdaki hazır örneklerden birini seçin..."
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 p-3 text-xs text-slate-200 placeholder-slate-500 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
            <div className="flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !inputText.trim()}
                className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 disabled:opacity-50 transition"
              >
                <Send className="h-3.5 w-3.5" />
                <span>{isLoading ? "Model Çalışıyor..." : "Moderasyon & Risk Analizini Çalıştır"}</span>
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
            <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              {/* Summary Header */}
              <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-3">
                <div>
                  <span className="text-xs text-slate-400">Moderasyon İnceleme Önceliği</span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span
                      className={`text-sm font-bold px-2.5 py-0.5 rounded-md ${
                        result.risk_vector.review_priority === "CRITICAL"
                          ? "bg-red-500/20 text-red-400 border border-red-500/40"
                          : result.risk_vector.review_priority === "HIGH"
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                          : result.risk_vector.review_priority === "MEDIUM"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                      }`}
                    >
                      {result.risk_vector.review_priority || result.risk_vector.risk_level} ÖNCELİK
                    </span>
                    <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-xs text-slate-300">
                      Bileşik Risk Skoru: {result.risk_vector.overall_risk_score}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] text-slate-400">İnsan Moderatör Tavsiyesi</span>
                  <div className="mt-0.5">
                    {result.risk_vector.human_review_recommended ? (
                      <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300 border border-amber-500/30 inline-flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        İnceleme Önerilir
                      </span>
                    ) : (
                      <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300 border border-emerald-500/30 inline-flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        Doğrudan Yayına Uygun
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Natural-Language Grounded Explanation */}
              {result.risk_vector.summary_explanation && (
                <div className="rounded-lg bg-slate-900/80 p-3 border border-slate-800 text-xs text-slate-300">
                  <span className="font-semibold text-slate-200">Gerekçeli Açıklama: </span>
                  {result.risk_vector.summary_explanation}
                </div>
              )}

              {/* 4 Multi-dimensional Risk Factors Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                    <LinkIcon className="h-3 w-3 text-blue-400" />
                    <span>Spam / Link</span>
                  </div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    %{ (result.risk_vector.spam_score * 100).toFixed(1) }
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                    <Copy className="h-3 w-3 text-cyan-400" />
                    <span>Şablon Tekrarı</span>
                  </div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    %{ (result.risk_vector.repetition_score * 100).toFixed(1) }
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                    <Users className="h-3 w-3 text-purple-400" />
                    <span>Koordineli Hesap</span>
                  </div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    %{ (result.risk_vector.coordination_score * 100).toFixed(1) }
                  </div>
                </div>
                <div className="rounded-lg bg-slate-900 p-2.5 border border-slate-800">
                  <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                    <Flame className="h-3 w-3 text-rose-400" />
                    <span>Model Güvensizlik</span>
                  </div>
                  <div className="font-mono font-bold text-slate-200 mt-1">
                    %{ (result.risk_vector.overall_risk_score * 100).toFixed(1) }
                  </div>
                </div>
              </div>

              {/* ModernBERT 11-Category Hazard Probabilities Breakdown */}
              {result.risk_vector.hazard_scores && (
                <div className="space-y-2 pt-2">
                  <div className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Activity className="h-4 w-4 text-indigo-400" />
                      <span>ModernBERT-TR Guardrail Risk Kategorileri (11 Sınıf)</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">Sigmoid Olasılıkları</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {Object.entries(result.risk_vector.hazard_scores).map(([catKey, prob]) => {
                      const probVal = Number(prob);
                      const isHigh = probVal >= 0.40;
                      return (
                        <div
                          key={catKey}
                          className="rounded-lg bg-slate-900/90 p-2 border border-slate-800/80 flex items-center justify-between"
                        >
                          <div className="flex-1 pr-2">
                            <div className="flex justify-between text-[11px] mb-1">
                              <span className="text-slate-300 font-medium">
                                {CATEGORY_NAMES_TR[catKey] || catKey}
                              </span>
                              <span className={`font-mono font-bold ${isHigh ? "text-rose-400" : "text-slate-400"}`}>
                                %{(probVal * 100).toFixed(1)}
                              </span>
                            </div>
                            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className={`h-full transition-all ${
                                  isHigh ? "bg-rose-500" : "bg-indigo-500/60"
                                }`}
                                style={{ width: `${Math.min(100, probVal * 100)}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Triggered Signals List */}
              <div className="space-y-2 pt-2">
                <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <FileCheck2 className="h-4 w-4 text-blue-400" />
                  <span>Tetiklenen Açıklanabilir Güvenlik Sinyalleri ({result.risk_vector.signals.length})</span>
                </div>

                {result.risk_vector.signals.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">
                    Herhangi bir risk, spam veya koordinasyon sinyali tetiklenmedi. Metin temiz görünüyor.
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
              <strong>Etik ve Şeffaf Moderasyon Prensibi:</strong> Bu analiz motoru içerikleri asla kesin olarak
              &quot;nefret söylemi&quot;, &quot;yasadışı&quot; veya &quot;bot&quot; olarak yaftalamaz. Yalnızca insan
              moderatörlere yardımcı olacak açıklanabilir risk göstergeleri ve kalibre edilmiş karar eşikleri üretir.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-800 bg-slate-950/80 px-5 py-3 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1 text-indigo-400/90">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Faz 2C Çok Boyutlu Moderasyon Motoru</span>
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
