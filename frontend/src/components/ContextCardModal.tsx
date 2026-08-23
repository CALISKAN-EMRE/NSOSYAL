"use client";

import React, { useState } from "react";
import { ContextCard } from "../lib/types";
import {
  X,
  Layers,
  Clock,
  BookOpen,
  Info,
  CheckCircle2,
  AlertCircle,
  FileText,
  Users,
  MessageSquare,
  Sparkles,
} from "lucide-react";

interface ContextCardModalProps {
  card: ContextCard | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading?: boolean;
}

export const ContextCardModal: React.FC<ContextCardModalProps> = ({
  card,
  isOpen,
  onClose,
  isLoading,
}) => {
  const [activeTab, setActiveTab] = useState<"perspectives" | "timeline" | "sources">("perspectives");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="relative flex max-h-[90vh] w-full max-w-3xl flex-col rounded-2xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-5 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                  Bağlam Kartı (Context Card)
                </span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400 border border-slate-700 font-mono">
                  {card?.topic_id}
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-100">{card?.topic_title || "Konu Bağlamı"}</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400 gap-3">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
              <p className="text-sm">Konu bağlamı sentezleniyor...</p>
            </div>
          ) : card ? (
            <>
              {/* Summary Section */}
              <div className="rounded-xl border border-blue-500/20 bg-blue-950/20 p-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 mb-1.5">
                  <Info className="h-4 w-4" />
                  <span>Konu Özeti ve Durum Tespiti</span>
                </div>
                <p className="text-sm leading-relaxed text-slate-200">{card.summary}</p>
                <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-400 border-t border-blue-500/10 pt-2">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3.5 w-3.5 text-blue-400" />
                    Toplam Gönderi: <strong className="text-slate-200">{card.total_posts}</strong>
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5 text-indigo-400" />
                    Katılımcı Sayısı: <strong className="text-slate-200">{card.total_participants}</strong>
                  </span>
                </div>
              </div>

              {/* Key Themes Pills */}
              {card.key_themes && card.key_themes.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Öne Çıkan Temalar & Etiketler
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {card.key_themes.map((theme, i) => (
                      <span
                        key={i}
                        className="rounded-lg bg-slate-800 px-2.5 py-1 text-xs text-slate-300 border border-slate-700"
                      >
                        #{theme}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Navigation Tabs */}
              <div className="flex border-b border-slate-800">
                <button
                  onClick={() => setActiveTab("perspectives")}
                  className={`flex items-center gap-2 border-b-2 px-4 py-2 text-xs font-medium transition ${
                    activeTab === "perspectives"
                      ? "border-blue-500 text-blue-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Users className="h-4 w-4" />
                  <span>Farklı Bakış Açıları ({card.perspectives.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("timeline")}
                  className={`flex items-center gap-2 border-b-2 px-4 py-2 text-xs font-medium transition ${
                    activeTab === "timeline"
                      ? "border-blue-500 text-blue-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Clock className="h-4 w-4" />
                  <span>Zaman Çizelgesi ({card.timeline.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("sources")}
                  className={`flex items-center gap-2 border-b-2 px-4 py-2 text-xs font-medium transition ${
                    activeTab === "sources"
                      ? "border-blue-500 text-blue-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <BookOpen className="h-4 w-4" />
                  <span>Kaynaklar ({card.sources.length})</span>
                </button>
              </div>

              {/* Tab 1: Perspectives */}
              {activeTab === "perspectives" && (
                <div className="space-y-3">
                  {card.perspectives.map((p, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-800 bg-slate-950/40 p-4 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {p.perspective_type === "supportive" ? (
                            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          ) : p.perspective_type === "critical" ? (
                            <AlertCircle className="h-4 w-4 text-amber-400" />
                          ) : (
                            <FileText className="h-4 w-4 text-blue-400" />
                          )}
                          <h4 className="text-sm font-semibold text-slate-200">{p.label}</h4>
                        </div>
                        <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                          {p.post_count} Paylaşım
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">{p.summary}</p>
                      {p.sample_quotes && p.sample_quotes.length > 0 && (
                        <div className="mt-2 space-y-1.5 border-t border-slate-800/60 pt-2">
                          <span className="text-[11px] font-semibold text-slate-400">Örnek İfadeler:</span>
                          {p.sample_quotes.map((q, qIdx) => (
                            <blockquote
                              key={qIdx}
                              className="border-l-2 border-slate-700 pl-2.5 text-xs italic text-slate-400"
                            >
                              &quot;{q}&quot;
                            </blockquote>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 2: Timeline */}
              {activeTab === "timeline" && (
                <div className="relative pl-6 space-y-4 border-l-2 border-slate-800 my-2">
                  {card.timeline.map((item, idx) => (
                    <div key={idx} className="relative group">
                      <div className="absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full border-2 border-slate-900 bg-blue-500" />
                      <div className="rounded-lg border border-slate-800 bg-slate-950/30 p-3">
                        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                          <span className="font-semibold text-blue-400">{item.title}</span>
                          <span className="font-mono text-[11px]">
                            {new Date(item.timestamp).toLocaleTimeString("tr-TR", {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300">{item.summary}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 3: Sources */}
              {activeTab === "sources" && (
                <div className="grid gap-3 sm:grid-cols-2">
                  {card.sources.map((src, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-800 bg-slate-950/40 p-3 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-slate-200">{src.source_name}</h4>
                        <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400 uppercase">
                          {src.source_type}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">{src.reliability_note}</p>
                      <div className="text-[10px] text-slate-500 pt-1">
                        Atıf Sayısı: {src.mention_count}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <p className="text-center text-sm text-slate-400">Bağlam kartı bilgisi bulunamadı.</p>
          )}
        </div>

        {/* Modal Footer & Prototype Notice */}
        <div className="border-t border-slate-800 bg-slate-950/80 px-5 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 text-amber-400/90">
            <Sparkles className="h-3.5 w-3.5 shrink-0" />
            <span>
              <strong>Yöntem:</strong> {card?.method || "Deterministik Metaveri Sentezleme (Faz 1 Prototip)"}
            </span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg bg-slate-800 px-4 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition self-end sm:self-auto"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};
