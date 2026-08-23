"use client";

import React from "react";
import { Topic } from "../lib/types";
import { Layers } from "lucide-react";

interface TopicFilterProps {
  topics: Topic[];
  selectedTopicId: string | null;
  onSelectTopic: (id: string | null) => void;
  totalPosts: number;
}

export const TopicFilter: React.FC<TopicFilterProps> = ({
  topics,
  selectedTopicId,
  onSelectTopic,
  totalPosts,
}) => {
  return (
    <div className="flex items-center gap-2 overflow-x-auto py-2 scrollbar-none">
      <button
        onClick={() => onSelectTopic(null)}
        className={`flex items-center gap-1.5 whitespace-nowrap rounded-full px-3.5 py-1.5 text-xs font-medium transition ${
          selectedTopicId === null
            ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
            : "border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800"
        }`}
      >
        <Layers className="h-3.5 w-3.5" />
        <span>Tüm Konular</span>
        <span
          className={`rounded-full px-1.5 py-0.2 text-[10px] ${
            selectedTopicId === null ? "bg-blue-700 text-white" : "bg-slate-800 text-slate-400"
          }`}
        >
          {totalPosts}
        </span>
      </button>

      {topics.map((topic) => {
        const isSelected = selectedTopicId === topic.id;
        return (
          <button
            key={topic.id}
            onClick={() => onSelectTopic(topic.id)}
            className={`flex items-center gap-1.5 whitespace-nowrap rounded-full px-3.5 py-1.5 text-xs font-medium transition ${
              isSelected
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800"
            }`}
          >
            <span>{topic.title}</span>
            <span
              className={`rounded-full px-1.5 py-0.2 text-[10px] ${
                isSelected ? "bg-blue-700 text-white" : "bg-slate-800 text-slate-400"
              }`}
            >
              {topic.post_count}
            </span>
          </button>
        );
      })}
    </div>
  );
};
