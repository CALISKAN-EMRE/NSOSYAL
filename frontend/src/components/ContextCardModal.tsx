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
  Zap,
  Activity,
  ShieldAlert,
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
  const [activeTab, setActiveTab] = useState<"perspectives" | "timeline" | "sources" | "timing">("perspectives");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
      <div className="relative flex max-h-[92vh] w-full max-w-3xl flex-col rounded-2xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-5 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
                    {card?.is_semantic_cluster ? (card?.semantic_cluster_id || "Semantik Küme") : "Statik Konu Filtresi"}
                  </span>
                  {card?.is_semantic_cluster && card?.cluster_membership_score !== undefined && card?.cluster_membership_score !== null && (
                    <span className="rounded-md bg-slate-800 px-2 py-0.5 text-xs font-medium text-slate-300 border border-slate-700">
                      Küme Üyelik Skoru (HDBSCAN): %{(card.cluster_membership_score * 100).toFixed(0)}
                    </span>
                  )}
                  {card?.is_semantic_cluster === false && (
                    <span className="rounded-md bg-amber-950/40 px-2 py-0.5 text-xs font-medium text-amber-300/80 border border-amber-800/40">
                      Geriye Dönük Uyumluluk (Filtre Modu)
                    </span>
                  )}
                  {card?.gated_spam_candidates_count !== undefined && card.gated_spam_candidates_count > 0 && (
                    <span className="rounded-md bg-amber-950/60 px-2 py-0.5 text-xs font-medium text-amber-300 border border-amber-800/50 flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3" />
                      {card.gated_spam_candidates_count} Spam Aday Elendi
                    </span>
                  )}
                </div>
              </div>
              <h2 className="text-lg font-bold text-slate-100 mt-0.5">
                {card?.topic_title || "Konu Bağlamı"}
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

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400 gap-3">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
              <p className="text-sm">Semantik küme ve kaynaklar sentezleniyor...</p>
            </div>
          ) : card ? (
            <>
              {/* Summary Section */}
              <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 mb-1.5">
                  <Info className="h-4 w-4" />
                  <span>Semantik Özet ve Durum Tespiti</span>
                </div>
                <p className="text-sm leading-relaxed text-slate-200">{card.summary}</p>
                <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-400 border-t border-indigo-500/10 pt-2">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3.5 w-3.5 text-indigo-400" />
                    Kümedeki Gönderi: <strong className="text-slate-200">{card.total_posts}</strong>
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5 text-blue-400" />
                    Katılımcı Sayısı: <strong className="text-slate-200">{card.total_participants}</strong>
                  </span>
                </div>
              </div>

              {/* Key Themes Pills */}
              {card.key_themes && card.key_themes.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Öne Çıkan Kavramlar & Temalar
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {card.key_themes.map((theme, i) => (
                      <span
                        key={i}
                        className="rounded-lg bg-slate-800/90 px-2.5 py-1 text-xs text-slate-300 border border-slate-700/70"
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
                      ? "border-indigo-500 text-indigo-400"
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
                      ? "border-indigo-500 text-indigo-400"
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
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <BookOpen className="h-4 w-4" />
                  <span>Yeniden Sıralı Kaynaklar ({card.sources.length})</span>
                </button>
                {card.pipeline_timing_ms && (
                  <button
                    onClick={() => setActiveTab("timing")}
                    className={`flex items-center gap-2 border-b-2 px-4 py-2 text-xs font-medium transition ${
                      activeTab === "timing"
                        ? "border-indigo-500 text-indigo-400"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <Activity className="h-4 w-4 text-emerald-400" />
                    <span>Gözlemlenebilirlik (Timing)</span>
                  </button>
                )}
              </div>

              {/* Tab 1: Perspectives */}
              {activeTab === "perspectives" && (
                <div className="space-y-3">
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                    <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>Perspektif Ayrıştırma Notu:</strong> Bu görünüm, külliyatın sentetik perspektif açıklamaları üzerinden gruplanmıştır. Otonom yapay zekâ duruş analizi iddiası taşımamaktadır.
                    </span>
                  </div>
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
                          <span className="text-[11px] font-semibold text-slate-400">
                            Kümeden Çıkarılan Kanıt İfadeleri:
                          </span>
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
                      <div className="absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full border-2 border-slate-900 bg-indigo-500" />
                      <div className="rounded-lg border border-slate-800 bg-slate-950/30 p-3">
                        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                          <span className="font-semibold text-indigo-400">{item.title}</span>
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

              {/* Tab 3: Two-Stage Reranked Sources */}
              {activeTab === "sources" && (
                <div className="space-y-3">
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>İki Aşamalı Erişim Notu:</strong> Kaynaklar önce <em>ModernBERT-TR Dense Retrieval</em> ile taranmış, ardından <em>ModernBERT Cross-Encoder Reranker</em> ile yeniden sıralanmıştır. Skorlar anlamsal uygunluğu gösterir; mutlak doğruluk/doğrulanmışlık garantisi vermez.
                    </span>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    {card.sources.map((src, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-800 bg-slate-950/40 p-3.5 space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5">
                            {src.rank && (
                              <span className="w-5 h-5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/50 flex items-center justify-center font-bold text-[10px]">
                                #{src.rank}
                              </span>
                            )}
                            <h4 className="text-xs font-semibold text-slate-200">{src.source_name}</h4>
                          </div>
                          <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400 uppercase">
                            {src.source_type}
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-400 leading-normal">{src.reliability_note}</p>

                        <div className="flex items-center justify-between pt-1.5 border-t border-slate-800/60 text-[11px]">
                          {src.relevance_score !== undefined && (
                            <span className="text-indigo-400 font-mono font-medium">
                              Reranker Skoru: %{(src.relevance_score * 100).toFixed(1)}
                            </span>
                          )}
                          {src.dense_score !== undefined && (
                            <span className="text-slate-400 font-mono text-[10px]">
                              Dense: %{(src.dense_score * 100).toFixed(1)}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 4: Observability & Timing */}
              {activeTab === "timing" && card.pipeline_timing_ms && (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400 uppercase font-medium">Kümeleme Süresi</div>
                      <div className="text-base font-bold text-slate-100 mt-1 font-mono">
                        {card.pipeline_timing_ms.clustering_ms ?? 0} ms
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400 uppercase font-medium">Yoğun Erişim (1. Aşama)</div>
                      <div className="text-base font-bold text-indigo-400 mt-1 font-mono">
                        {card.pipeline_timing_ms.dense_retrieval_ms ?? 0} ms
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400 uppercase font-medium">Reranker (2. Aşama)</div>
                      <div className="text-base font-bold text-emerald-400 mt-1 font-mono">
                        {card.pipeline_timing_ms.reranking_ms ?? 0} ms
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400 uppercase font-medium">Toplam Boru Hattı</div>
                      <div className="text-base font-bold text-amber-400 mt-1 font-mono">
                        {card.pipeline_timing_ms.total_pipeline_ms ?? 0} ms
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800/80 text-xs text-slate-400 space-y-1">
                    <div><strong>Kullanılan Modeller:</strong> {card.model_used || "ModernBERT Pipeline"}</div>
                    <div><strong>Yöntem:</strong> {card.method}</div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-center text-sm text-slate-400">Bağlam kartı bilgisi bulunamadı.</p>
          )}
        </div>

        {/* Modal Footer */}
        <div className="border-t border-slate-800 bg-slate-950/80 px-5 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 text-indigo-400">
            <Sparkles className="h-3.5 w-3.5 shrink-0" />
            <span>
              <strong>Yöntem:</strong> {card?.method || "ModernBERT Semantic Pipeline"}
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
