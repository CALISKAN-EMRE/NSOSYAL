"use client";

import React, { useEffect, useState, useCallback } from "react";
import { api } from "../lib/api";
import {
  ContextCard,
  Post,
  RecommendationExplanation,
  RecommendedPost,
  SearchResultItem,
  SystemHealth,
  Topic,
} from "../lib/types";
import { Header } from "../components/Header";
import { TopicFilter } from "../components/TopicFilter";
import { Feed } from "../components/Feed";
import { ContextCardModal } from "../components/ContextCardModal";
import { ExplainModal } from "../components/ExplainModal";
import { SafetyAuditPanel } from "../components/SafetyAuditPanel";
import {
  Layers,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  Info,
  Search,
  Cpu,
} from "lucide-react";

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [recommendedPosts, setRecommendedPosts] = useState<RecommendedPost[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);

  const [selectedTopicId, setSelectedTopicId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Modals state
  const [contextCard, setContextCard] = useState<ContextCard | null>(null);
  const [isContextModalOpen, setIsContextModalOpen] = useState(false);
  const [isContextLoading, setIsContextLoading] = useState(false);

  const [explainPost, setExplainPost] = useState<Post | null>(null);
  const [explanation, setExplanation] = useState<RecommendationExplanation | null>(null);
  const [isExplainModalOpen, setIsExplainModalOpen] = useState(false);

  const [isSafetyPanelOpen, setIsSafetyPanelOpen] = useState(false);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [topicsData, rawPostsData, recPostsData, healthData] = await Promise.allSettled([
        api.getTopics(),
        api.getPosts({ topic_id: selectedTopicId || undefined, search: searchQuery || undefined }),
        api.getRecommendations({ preferred_topic: selectedTopicId || undefined }),
        api.getHealth(),
      ]);

      if (topicsData.status === "fulfilled") setTopics(topicsData.value);
      if (rawPostsData.status === "fulfilled") setPosts(rawPostsData.value);
      if (recPostsData.status === "fulfilled") setRecommendedPosts(recPostsData.value);
      if (healthData.status === "fulfilled") setHealth(healthData.value);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedTopicId, searchQuery]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleViewContext = async (topicId: string) => {
    setIsContextModalOpen(true);
    setIsContextLoading(true);
    try {
      const card = await api.getContextCard(topicId);
      setContextCard(card);
    } catch (err) {
      console.error("Failed to load context card:", err);
      setContextCard(null);
    } finally {
      setIsContextLoading(false);
    }
  };

  const handleViewExplanation = (post: Post, exp: RecommendationExplanation) => {
    setExplainPost(post);
    setExplanation(exp);
    setIsExplainModalOpen(true);
  };

  const handleSelectSearchResult = (result: SearchResultItem) => {
    if (result.post.topic_id) {
      handleViewContext(result.post.topic_id);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onOpenSafetyPanel={() => setIsSafetyPanelOpen(true)}
        onSelectSearchResult={handleSelectSearchResult}
        adapterStatus={health?.data_source_adapter?.adapter_type || "JsonDemoAdapter"}
        postCount={posts.length}
      />

      {/* Main Content Layout */}
      <main className="mx-auto max-w-6xl flex-1 px-4 py-6 sm:px-6 w-full">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          {/* Left Sidebar: Architecture & Core Pillars */}
          <aside className="lg:col-span-4 space-y-4">
            {/* Project Overview Card */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm space-y-4">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Info className="h-4 w-4" />
                </span>
                <h2 className="text-sm font-bold text-slate-100">Faz 2B Semantik Yetenekler</h2>
              </div>

              <div className="space-y-3 text-xs text-slate-300">
                <div className="flex gap-2.5 rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                  <Layers className="h-4 w-4 shrink-0 text-indigo-400 mt-0.5" />
                  <div>
                    <strong className="text-slate-100 block">1. Semantik Kümeleme (ModernBERT + HDBSCAN)</strong>
                    <span>Metinleri otomatik gruplar, çoklu perspektif ve özet sentezler.</span>
                  </div>
                </div>

                <div className="flex gap-2.5 rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                  <Cpu className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                  <div>
                    <strong className="text-slate-100 block">2. İki Aşamalı Reranker (ModernBERT-TR)</strong>
                    <span>Yoğun arama ile ilk 15 adayı seçer, Cross-Encoder ile yeniden sıralar.</span>
                  </div>
                </div>

                <div className="flex gap-2.5 rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                  <Search className="h-4 w-4 shrink-0 text-blue-400 mt-0.5" />
                  <div>
                    <strong className="text-slate-100 block">3. Doğal Dil Arama (Multilingual-E5)</strong>
                    <span>Türkçe soru ve sorgularla doğrudan anlamsal eşleşme sağlar.</span>
                  </div>
                </div>

                <div className="flex gap-2.5 rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                  <HelpCircle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
                  <div>
                    <strong className="text-slate-100 block">4. Şeffaf Tavsiye & Anlamsal İlgi</strong>
                    <span>Embedding kosinüs benzerliği ile &quot;Neden bunu görüyorum?&quot; faktörlerini açıklar.</span>
                  </div>
                </div>

                <div className="flex gap-2.5 rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                  <ShieldAlert className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
                  <div>
                    <strong className="text-slate-100 block">5. Güvenlik ve Moderasyon Sinyalleri</strong>
                    <span>Spam ve koordinasyon risklerini insan denetimli sinyallerle puanlar.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Production Architecture Notice Box */}
            <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-4 text-xs text-slate-300 space-y-2">
              <div className="flex items-center gap-2 font-semibold text-indigo-400">
                <Sparkles className="h-4 w-4" />
                <span>TEKNOFEST 2026 Üretim Notu</span>
              </div>
              <p className="text-[11px] leading-relaxed text-slate-400">
                Bu prototipte <strong>ModernBERT-TR</strong>, <strong>ModernBERT-TR-Guardrail</strong> ve <strong>Multilingual-E5</strong> modelleri
                doğrudan yerel GPU üzerinde çalışmaktadır. Gerçek zamanlı arama, kümeleme, yeniden sıralama ve içerik güvenliği aktiftir.
              </p>
            </div>
          </aside>

          {/* Center Column: Topic Filters & Post Feed */}
          <section className="lg:col-span-8 space-y-4">
            {/* Topic Filter Pills */}
            <TopicFilter
              topics={topics}
              selectedTopicId={selectedTopicId}
              onSelectTopic={setSelectedTopicId}
              totalPosts={posts.length}
            />

            {/* Feed */}
            <Feed
              recommendedPosts={recommendedPosts}
              rawPosts={posts}
              isLoading={isLoading}
              onRefresh={loadData}
              onViewContext={handleViewContext}
              onViewExplanation={handleViewExplanation}
            />
          </section>
        </div>
      </main>

      {/* Modals */}
      <ContextCardModal
        card={contextCard}
        isOpen={isContextModalOpen}
        onClose={() => setIsContextModalOpen(false)}
        isLoading={isContextLoading}
      />

      <ExplainModal
        post={explainPost}
        explanation={explanation}
        isOpen={isExplainModalOpen}
        onClose={() => setIsExplainModalOpen(false)}
      />

      <SafetyAuditPanel
        isOpen={isSafetyPanelOpen}
        onClose={() => setIsSafetyPanelOpen(false)}
      />
    </div>
  );
}
