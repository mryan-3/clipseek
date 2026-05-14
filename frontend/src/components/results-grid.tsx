"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface SearchResult {
  id: string;
  score: number;
  frame_url: string;
  metadata: {
    timestamp: number;
    filename: string;
    video_id: string;
  };
}

interface ResultsGridProps {
  results: SearchResult[];
  onResultClick: (timestamp: number) => void;
  isLoading?: boolean;
}

export function ResultsGrid({ results, onResultClick, isLoading }: ResultsGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-12">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="aspect-video bg-black/5 animate-pulse rounded-xl" />
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-24 reveal">
        <p className="text-text-muted text-sm tracking-tight">No moments found. Try indexing a video or searching for a different term.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-12 mb-24 reveal">
      {results.map((result) => (
        <button
          key={result.id}
          onClick={() => onResultClick(result.metadata.timestamp)}
          className="group relative text-left transition-all active:scale-[0.98]"
        >
          <div className="aspect-video relative overflow-hidden rounded-xl border border-border-subtle bg-canvas">
            {/* 
              We assume the backend is running on localhost:8000.
              In production, this would be an environment variable.
            */}
            <img
              src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${result.frame_url}`}
              alt={`Moment at ${result.metadata.timestamp}s`}
              className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-black/0 transition-colors group-hover:bg-black/5" />
            <div className="absolute bottom-2 right-2 px-2 py-1 bg-white/90 backdrop-blur-sm rounded-md border border-border-subtle text-[10px] font-mono font-medium shadow-sm">
              {formatTimestamp(result.metadata.timestamp)}
            </div>
          </div>
          <div className="mt-3 px-1">
            <div className="flex justify-end items-center">
              <span className="text-[10px] uppercase tracking-widest text-text-muted">
                Jump to
              </span>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

function formatTimestamp(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h > 0 ? h : null, m, s]
    .filter((x) => x !== null)
    .map((x) => (x! < 10 ? `0${x}` : x))
    .join(":");
}
