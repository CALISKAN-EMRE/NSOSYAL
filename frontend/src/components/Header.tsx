"use client";

import React, { useEffect, useState } from "react";
import { Compass, ShieldCheck, Sparkles, Database, Cpu, Zap } from "lucide-react";
import { SemanticSearchBar } from "./SemanticSearchBar";
import { SearchResultItem, SystemStatusResponse } from "../lib/types";
import { api } from "../lib/api";

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (val: string) => void;
  onOpenSafetyPanel: () => void;
  onSelectSearchResult?: (result: SearchResultItem) => void;
  adapterStatus?: string;
  postCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  onOpenSafetyPanel,
  onSelectSearchResult,
  adapterStatus = "JsonDemoAdapter",
  postCount,
}) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);

  useEffect(() => {
    api
      .getSystemStatus()
      .then((data) => setSystemStatus(data))
      .catch((err) => console.error("Could not fetch system status:", err));
  }, []);

  const isML = systemStatus?.model_manager?.semantic_mode === "ml";
  const device = systemStatus?.model_manager?.device || "cpu";

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-[#090d16]/95 backdrop-blur-md">
      <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Logo & Project Title */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-blue-700 text-white shadow-lg shadow-indigo-500/20">
              <Compass className="h-6 w-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-white sm:text-xl">
                  NSosyal Pusula
                </h1>
                <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
                  TEKNOFEST 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi
              </p>
            </div>
          </div>

          {/* Natural Language Semantic Search Bar */}
          <div className="flex-1 max-w-xl mx-auto md:mx-4">
            <SemanticSearchBar
              onSelectSearchResult={onSelectSearchResult}
              onClearSearch={() => onSearchChange("")}
            />
          </div>

          {/* Safety Sandbox Trigger */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenSafetyPanel}
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/10 hover:text-emerald-300 shadow-sm"
              title="Canlı metin güvenlik ve moderasyon analiz motorunu test edin"
            >
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span className="hidden sm:inline">Güvenlik Lab</span>
            </button>
          </div>
        </div>

        {/* Prototype & Model Status Bar */}
        <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/60 pt-2 text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-slate-300">
              <Database className="h-3.5 w-3.5 text-blue-400" />
              Adaptör: <span className="font-mono text-blue-400">{adapterStatus}</span>
            </span>
            <span>•</span>
            <span>{postCount} Gönderi</span>
          </div>

          <div className="flex items-center gap-2">
            {isML ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 font-medium">
                <Cpu className="h-3 w-3 text-emerald-400" />
                ML Mod: ModernBERT + E5 ({device.toUpperCase()})
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-950/60 text-amber-300 border border-amber-800/50 font-medium">
                <Zap className="h-3 w-3 text-amber-400" />
                Mod: Demo Deterministik
              </span>
            )}
            <span className="text-slate-400">
              Faz 2B Semantik Mimari
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
