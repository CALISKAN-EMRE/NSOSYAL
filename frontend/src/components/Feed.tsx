"use client";

import React, { useState } from "react";
import { Post, RecommendedPost, RecommendationExplanation } from "../lib/types";
import { PostCard } from "./PostCard";
import { Sparkles, Clock, AlertTriangle, RefreshCw } from "lucide-react";

interface FeedProps {
  recommendedPosts: RecommendedPost[];
  rawPosts: Post[];
  isLoading: boolean;
  onRefresh: () => void;
  onViewContext: (topicId: string) => void;
  onViewExplanation: (post: Post, exp: RecommendationExplanation) => void;
}

export const Feed: React.FC<FeedProps> = ({
  recommendedPosts,
  rawPosts,
  isLoading,
  onRefresh,
  onViewContext,
  onViewExplanation,
}) => {
  const [feedMode, setFeedMode] = useState<"recommended" | "chronological" | "risk">("recommended");

  const filteredPosts = () => {
    if (feedMode === "recommended") {
      return recommendedPosts.map((r) => ({
        post: r.post,
        explanation: r.explanation,
      }));
    } else if (feedMode === "chronological") {
      return rawPosts.map((p) => {
        const matchingRec = recommendedPosts.find((r) => r.post.id === p.id);
        return {
          post: p,
          explanation: matchingRec?.explanation,
        };
      });
    } else {
      // Risk tab: only posts with MEDIUM or HIGH safety risk
      return rawPosts
        .filter((p) => p.safety_risk_level === "HIGH" || p.safety_risk_level === "MEDIUM")
        .map((p) => {
          const matchingRec = recommendedPosts.find((r) => r.post.id === p.id);
          return {
            post: p,
            explanation: matchingRec?.explanation,
          };
        });
    }
  };

  const displayList = filteredPosts();

  return (
    <div className="space-y-4">
      {/* Feed Mode Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-1 rounded-xl bg-slate-900/90 p-1 border border-slate-800">
          <button
            onClick={() => setFeedMode("recommended")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
              feedMode === "recommended"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Şeffaf Önerilen Akış</span>
          </button>

          <button
            onClick={() => setFeedMode("chronological")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
              feedMode === "chronological"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Clock className="h-3.5 w-3.5" />
            <span>Tüm Paylaşımlar</span>
          </button>

          <button
            onClick={() => setFeedMode("risk")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
              feedMode === "risk"
                ? "bg-amber-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>Riskli / Moderasyon</span>
          </button>
        </div>

        <button
          onClick={onRefresh}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-blue-400 transition"
          title="Akışı Yenile"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Yenile</span>
        </button>
      </div>

      {/* Feed List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="animate-pulse rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-3"
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-slate-800" />
                <div className="space-y-1.5">
                  <div className="h-4 w-28 rounded bg-slate-800" />
                  <div className="h-3 w-20 rounded bg-slate-800" />
                </div>
              </div>
              <div className="h-3 w-full rounded bg-slate-800" />
              <div className="h-3 w-4/5 rounded bg-slate-800" />
            </div>
          ))}
        </div>
      ) : displayList.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-950/40 p-12 text-center text-slate-400 space-y-2">
          <p className="text-sm">Bu filtreye uygun gönderi bulunamadı.</p>
          <p className="text-xs text-slate-500">
            Arama kriterinizi değiştirebilir veya tüm konuları seçebilirsiniz.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayList.map(({ post, explanation }) => (
            <PostCard
              key={post.id}
              post={post}
              explanation={explanation}
              onViewContext={onViewContext}
              onViewExplanation={onViewExplanation}
            />
          ))}
        </div>
      )}
    </div>
  );
};
