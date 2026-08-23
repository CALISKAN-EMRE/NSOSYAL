"use client";

import React from "react";
import { Post, RecommendationExplanation } from "../lib/types";
import { X, HelpCircle, ArrowUpRight, ArrowDownRight, Sparkles, Calculator } from "lucide-react";

interface ExplainModalProps {
  post: Post | null;
  explanation: RecommendationExplanation | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainModal: React.FC<ExplainModalProps> = ({
  post,
  explanation,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !post || !explanation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="relative flex max-h-[90vh] w-full max-w-2xl flex-col rounded-2xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-slate-800 p-5 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <HelpCircle className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                Şeffaf Tavsiye Gerekçesi
              </span>
              <h2 className="text-lg font-bold text-slate-100">Neden Bunu Görüyorum?</h2>
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
          {/* Post Snippet */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3.5">
            <div className="flex items-center gap-2 mb-1">
              <strong className="text-xs font-semibold text-slate-300">{post.author.name}</strong>
              <span className="text-[11px] font-mono text-slate-500">{post.author.handle}</span>
            </div>
            <p className="text-xs text-slate-300 line-clamp-2 italic">&quot;{post.text}&quot;</p>
          </div>

          {/* Final Score Banner */}
          <div className="flex items-center justify-between rounded-xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/30 to-blue-950/30 p-4">
            <div>
              <div className="text-xs text-indigo-300 font-medium">Toplam Tavsiye Uygunluk Puanı</div>
              <div className="text-xs text-slate-400 mt-1 max-w-sm">{explanation.summary_reason}</div>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold text-indigo-400 font-mono">
                {explanation.final_score.toFixed(0)}
              </span>
              <span className="text-xs text-slate-400"> / 100</span>
            </div>
          </div>

          {/* Score Factors Breakdown */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Puanlama Bileşenleri & Katsayılar
              </h4>
              <span className="text-[11px] text-slate-500">Açıklanabilir Doğrusal Model</span>
            </div>

            <div className="space-y-2.5">
              {explanation.factors.map((factor, idx) => {
                const isPenalty = factor.is_penalty;
                return (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-800/80 bg-slate-950/30 p-3 space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5 font-medium text-slate-200">
                        {isPenalty ? (
                          <ArrowDownRight className="h-3.5 w-3.5 text-red-400" />
                        ) : (
                          <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
                        )}
                        <span>{factor.label}</span>
                        <span className="rounded bg-slate-800 px-1.5 py-0.2 text-[10px] text-slate-400 font-mono">
                          Ağırlık: {factor.weight}
                        </span>
                      </div>
                      <span
                        className={`font-mono text-xs font-bold ${
                          isPenalty
                            ? factor.weighted_impact < 0
                              ? "text-red-400"
                              : "text-slate-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {factor.weighted_impact > 0 ? `+${factor.weighted_impact}` : factor.weighted_impact} p
                      </span>
                    </div>

                    {/* Progress indicator */}
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                      <div
                        className={`h-full rounded-full ${
                          isPenalty ? "bg-red-500" : "bg-emerald-500"
                        }`}
                        style={{ width: `${Math.min(100, Math.max(5, factor.raw_score * 100))}%` }}
                      />
                    </div>

                    <p className="text-[11px] text-slate-400">{factor.explanation}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mathematical Formula Footnote */}
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-[11px] text-slate-400 space-y-1">
            <div className="flex items-center gap-1.5 text-slate-300 font-medium">
              <Calculator className="h-3.5 w-3.5 text-blue-400" />
              <span>Şeffaf Öneri Fonksiyonu:</span>
            </div>
            <p className="font-mono text-[10px] text-slate-300 bg-slate-900 p-2 rounded border border-slate-800">
              Skor = (30·İlgi + 25·Konu + 20·Güncellik + 15·Çeşitlilik) - (20·TekrarCezası + 30·GüvenlikCezası)
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="border-t border-slate-800 bg-slate-950/80 px-5 py-3 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1 text-amber-400/90">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Faz 1 Kural ve Sezgisel Açıklama Motoru</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg bg-slate-800 px-4 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            Anladım
          </button>
        </div>
      </div>
    </div>
  );
};
