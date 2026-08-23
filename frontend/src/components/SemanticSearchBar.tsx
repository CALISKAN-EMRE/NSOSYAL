"use client";

import React, { useState, useEffect } from "react";
import { Search, Sparkles, X, Clock, Zap } from "lucide-react";
import { api } from "../lib/api";
import { SearchResponse, SearchResultItem } from "../lib/types";

interface SemanticSearchBarProps {
  onSelectSearchResult?: (result: SearchResultItem) => void;
  onClearSearch?: () => void;
}

const SAMPLE_QUERIES = [
  "Otoyollarda elektrikli araç şarjı",
  "Yapay zeka eğitimde öğretmen rolü",
  "Kamu kurumlarında açık kaynak ve Pardus",
  "Otonom araçlarda kaza sorumluluğu",
];

export function SemanticSearchBar({
  onSelectSearchResult,
  onClearSearch,
}: SemanticSearchBarProps) {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResponse(null);
      setIsOpen(false);
      if (onClearSearch) onClearSearch();
      return;
    }

    setIsLoading(true);
    setIsOpen(true);
    try {
      const resp = await api.searchPosts(searchQuery.trim(), 10);
      setSearchResponse(resp);
    } catch (err) {
      console.error("Semantic search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setQuery("");
    setSearchResponse(null);
    setIsOpen(false);
    if (onClearSearch) onClearSearch();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch(query);
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* Search Input Box */}
      <div className="relative flex items-center">
        <div className="absolute left-3.5 text-indigo-400 pointer-events-none flex items-center gap-1">
          <Search className="w-4 h-4" />
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Doğal dilde anlamsal ara (Örn: 'kamuda açık kaynak yazılım', 'şarj istasyonları')..."
          className="w-full pl-10 pr-24 py-2.5 bg-slate-900/90 hover:bg-slate-900 text-slate-100 placeholder-slate-400 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 shadow-inner outline-none transition-all"
        />

        <div className="absolute right-2.5 flex items-center gap-1.5">
          {query && (
            <button
              onClick={handleClear}
              className="p-1 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-md transition-colors"
              title="Temizle"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          <button
            onClick={() => handleSearch(query)}
            disabled={isLoading || !query.trim()}
            className="flex items-center gap-1 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg shadow-sm transition-all"
          >
            {isLoading ? (
              <span className="animate-spin text-xs">⏳</span>
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>Ara</span>
          </button>
        </div>
      </div>

      {/* Suggested Quick Queries */}
      {!isOpen && !query && (
        <div className="flex items-center gap-1.5 mt-2 overflow-x-auto pb-1 text-xs text-slate-400">
          <span className="text-[11px] text-slate-400 font-medium shrink-0">Hızlı Sorular:</span>
          {SAMPLE_QUERIES.map((sq, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="px-2.5 py-1 bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-indigo-300 rounded-full border border-slate-700/60 text-[11px] shrink-0 transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>
      )}

      {/* Search Results Dropdown / Modal List */}
      {isOpen && searchResponse && (
        <div className="absolute z-50 left-0 right-0 mt-2 bg-slate-900 border border-slate-700/90 rounded-xl shadow-2xl overflow-hidden backdrop-blur-md">
          {/* Header */}
          <div className="px-4 py-2.5 bg-slate-800/80 border-b border-slate-700/60 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-300 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>
                "{searchResponse.query}" için <strong>{searchResponse.total_results}</strong> sonuç
              </span>
            </div>
            <div className="flex items-center gap-2 text-slate-400 text-[11px]">
              <span className="flex items-center gap-1 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                <Zap className="w-3 h-3 text-amber-400" />
                {searchResponse.model_used.includes("multilingual-e5") ? "Multilingual-E5-Instruct" : "Demo Embed"}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {searchResponse.search_latency_ms} ms
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-200 ml-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Results list */}
          <div className="max-h-96 overflow-y-auto divide-y divide-slate-800/70 p-1">
            {searchResponse.results.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-xs">
                Eşleşen anlamlı gönderi bulunamadı. Lütfen sorgunuzu genişletin.
              </div>
            ) : (
              searchResponse.results.map((item) => (
                <div
                  key={item.post.id}
                  onClick={() => {
                    if (onSelectSearchResult) onSelectSearchResult(item);
                  }}
                  className="p-3 hover:bg-slate-800/60 rounded-lg cursor-pointer transition-colors group"
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className="w-5 h-5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/50 flex items-center justify-center font-bold text-[10px]">
                        #{item.rank}
                      </span>
                      <span className="font-semibold text-slate-200">
                        {item.post.author.name}
                      </span>
                      <span className="text-slate-400 text-[11px]">
                        {item.post.author.handle}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 bg-indigo-950/70 text-indigo-300 border border-indigo-800/50 text-[10px] font-mono rounded-md">
                        Benzerlik: %{(item.relevance_score * 100).toFixed(1)}
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-300 text-xs leading-relaxed line-clamp-2">
                    {item.post.text}
                  </p>

                  <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-400">
                    <span className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">
                      {item.post.topic_title}
                    </span>
                    {item.post.tags.slice(0, 3).map((tag, tIdx) => (
                      <span key={tIdx} className="text-slate-400">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
