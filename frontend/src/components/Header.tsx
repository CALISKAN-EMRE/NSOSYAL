"use client";

import React from "react";
import { Compass, ShieldCheck, Sparkles, Search, Database } from "lucide-react";

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (val: string) => void;
  onOpenSafetyPanel: () => void;
  adapterStatus?: string;
  postCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  onOpenSafetyPanel,
  adapterStatus = "JsonDemoAdapter",
  postCount,
}) => {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-[#090d16]/90 backdrop-blur-md">
      <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Logo & Project Title */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-lg shadow-blue-500/20">
              <Compass className="h-6 w-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-white sm:text-xl">
                  NSosyal Pusula
                </h1>
                <span className="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-semibold text-blue-400 border border-blue-500/20">
                  TEKNOFEST 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi
              </p>
            </div>
          </div>

          {/* Search & Actions */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Search Input */}
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Paylaşım veya etiket ara..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900/80 py-1.5 pl-9 pr-3 text-xs text-slate-200 placeholder-slate-500 outline-none transition focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Safety Sandbox Trigger */}
            <button
              onClick={onOpenSafetyPanel}
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/10 hover:text-emerald-300"
              title="Canlı metin güvenlik ve moderasyon analiz motorunu test edin"
            >
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span className="hidden sm:inline">Güvenlik Laboratuvarı</span>
            </button>
          </div>
        </div>

        {/* Prototype Status Bar */}
        <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/60 pt-2 text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-slate-300">
              <Database className="h-3.5 w-3.5 text-blue-400" />
              Adaptör: <span className="font-mono text-blue-400">{adapterStatus}</span>
            </span>
            <span>•</span>
            <span>{postCount} Sentetik Gönderi</span>
          </div>

          <div className="flex items-center gap-1.5 text-amber-300/90">
            <Sparkles className="h-3 w-3" />
            <span>Faz 1 Dikey Kesit (Kural ve Sezgisel Demo Sinyalleri)</span>
          </div>
        </div>
      </div>
    </header>
  );
};
