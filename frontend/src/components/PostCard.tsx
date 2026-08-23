"use client";

import React from "react";
import { Post, RecommendationExplanation } from "../lib/types";
import {
  Sparkles,
  Layers,
  Heart,
  Repeat2,
  MessageCircle,
  AlertTriangle,
  HelpCircle,
  Tag,
} from "lucide-react";

interface PostCardProps {
  post: Post;
  explanation?: RecommendationExplanation;
  onViewContext: (topicId: string) => void;
  onViewExplanation: (post: Post, exp: RecommendationExplanation) => void;
}

export const PostCard: React.FC<PostCardProps> = ({
  post,
  explanation,
  onViewContext,
  onViewExplanation,
}) => {
  const getSourceBadgeColor = (sourceType: string) => {
    switch (sourceType) {
      case "official_source":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "academic":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "news_outlet":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "expert":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "community":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  const getSourceLabel = (sourceType: string) => {
    switch (sourceType) {
      case "official_source":
        return "Resmi Kurum";
      case "academic":
        return "Akademik";
      case "news_outlet":
        return "Haber Kaynağı";
      case "expert":
        return "Uzman";
      case "community":
        return "Topluluk";
      default:
        return "Kullanıcı";
    }
  };

  const isHighRisk = post.safety_risk_level === "HIGH";
  const isMediumRisk = post.safety_risk_level === "MEDIUM";

  return (
    <article
      className={`rounded-2xl border transition hover:border-slate-700 ${
        isHighRisk
          ? "border-red-900/40 bg-red-950/10"
          : isMediumRisk
          ? "border-amber-900/40 bg-amber-950/10"
          : "border-slate-800/80 bg-slate-900/50"
      } p-4 sm:p-5 backdrop-blur-sm`}
    >
      {/* Card Header: Author & Source */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          <div className="relative h-10 w-10 overflow-hidden rounded-full bg-slate-800 border border-slate-700">
            {post.author.avatar ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={post.author.avatar}
                alt={post.author.name}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center font-bold text-slate-400">
                {post.author.name.charAt(0)}
              </div>
            )}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-1.5">
              <h3 className="font-semibold text-slate-100 text-sm">{post.author.name}</h3>
              {post.author.badge && (
                <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-300 border border-slate-700">
                  {post.author.badge}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">{post.author.handle}</p>
          </div>
        </div>

        {/* Source Badge */}
        <span
          className={`rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${getSourceBadgeColor(
            post.source_type
          )}`}
        >
          {getSourceLabel(post.source_type)}
        </span>
      </div>

      {/* Safety Risk Alert Banner if flagged */}
      {(isHighRisk || isMediumRisk) && (
        <div className="mt-3 flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-300">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
          <span>
            {isHighRisk
              ? "Yüksek spam / şablon tekrarı sinyali tespit edildi (Moderasyon İncelemesi Önerilir)."
              : "Biçim veya tekrar anomalisi sinyali saptandı (Sezgisel Kontrol)."}
          </span>
        </div>
      )}

      {/* Post Text */}
      <p className="mt-3 text-sm leading-relaxed text-slate-200 whitespace-pre-line">
        {post.text}
      </p>

      {/* Tags */}
      {post.tags && post.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {post.tags.map((tag, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 rounded bg-slate-800/80 px-2 py-0.5 text-[11px] text-slate-400"
            >
              <Tag className="h-2.5 w-2.5 text-slate-500" />
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer: Engagement & Transparent Actions */}
      <div className="mt-4 flex flex-col gap-3 border-t border-slate-800/60 pt-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Engagement Stats */}
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-1 hover:text-red-400 transition cursor-pointer">
            <Heart className="h-3.5 w-3.5" />
            <span>{post.metrics?.likes || 0}</span>
          </div>
          <div className="flex items-center gap-1 hover:text-green-400 transition cursor-pointer">
            <Repeat2 className="h-3.5 w-3.5" />
            <span>{post.metrics?.reposts || 0}</span>
          </div>
          <div className="flex items-center gap-1 hover:text-blue-400 transition cursor-pointer">
            <MessageCircle className="h-3.5 w-3.5" />
            <span>{post.metrics?.replies || 0}</span>
          </div>
        </div>

        {/* Intelligence Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Why am I seeing this? */}
          {explanation && (
            <button
              onClick={() => onViewExplanation(post, explanation)}
              className="flex items-center gap-1 rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1 text-xs font-medium text-indigo-300 hover:bg-indigo-500/20 transition"
              title="Öneri puanlama bileşenlerini ve gerekçesini inceleyin"
            >
              <HelpCircle className="h-3.5 w-3.5" />
              <span>Neden Görüyorum?</span>
              <span className="ml-1 rounded bg-indigo-500/20 px-1 py-0.2 text-[10px] font-mono text-indigo-200">
                {explanation.final_score.toFixed(0)}p
              </span>
            </button>
          )}

          {/* Context Card Trigger */}
          <button
            onClick={() => onViewContext(post.topic_id)}
            className="flex items-center gap-1 rounded-lg border border-blue-500/30 bg-blue-600/10 px-2.5 py-1 text-xs font-medium text-blue-300 hover:bg-blue-600/20 transition"
            title="Konunun tarafsız özetini, farklı bakış açılarını ve zaman çizelgesini görüntüleyin"
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Bağlamı Gör</span>
          </button>
        </div>
      </div>
    </article>
  );
};
