"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

interface VideoLinkProps {
  onLink: (path: string) => void;
  isLoading?: boolean;
}

export function VideoLink({ onLink, isLoading }: VideoLinkProps) {
  const [path, setPath] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (path.trim()) onLink(path.trim());
  };

  return (
    <div className="w-full max-w-xl mx-auto reveal">
      <div className="rounded-2xl bg-white border border-clay p-8 shadow-sm">
        <h2 className="text-2xl text-ink mb-2">Begin your collection</h2>
        <p className="text-sm text-ink/60 mb-6">Paste the local path to your video file.</p>
        
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="/path/to/video.mp4"
            className="flex-1 bg-canvas border border-clay rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-accent transition-colors"
          />
          <button
            type="submit"
            disabled={isLoading || !path.trim()}
            className="px-6 py-3 bg-ink text-canvas rounded-xl text-sm font-bold transition-transform active:scale-95 disabled:opacity-30"
          >
            {isLoading ? "..." : "Link"}
          </button>
        </form>
      </div>
    </div>
  );
}
