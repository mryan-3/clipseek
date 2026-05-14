"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface StatusCardProps {
  status: string | null;
  videoId: string;
  onReset: () => void;
}

export function StatusCard({ status, videoId, onReset }: StatusCardProps) {
  const isCompleted = status === "completed";
  
  return (
    <div className="max-w-xl mx-auto reveal">
      <div className="flex items-center justify-between p-6 bg-white rounded-2xl border border-clay shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-canvas flex items-center justify-center border border-clay">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 7l-7 5 7 5V7z" /><rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
          </div>
          <div className="overflow-hidden">
            <h3 className="text-sm font-bold text-ink truncate">Your Video</h3>
            <p className="text-[10px] text-ink/40 font-mono truncate">{videoId}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className={cn(
            "text-[10px] uppercase tracking-widest font-bold px-3 py-1 rounded-full border",
            isCompleted ? "bg-green-50 border-green-100 text-green-700" : "bg-accent/10 border-accent/20 text-accent"
          )}>
            {status?.replace("_", " ")}
          </span>
          <button onClick={onReset} className="p-2 hover:bg-canvas rounded-full transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
