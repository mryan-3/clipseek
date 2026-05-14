"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  onSearch: (query: string) => void;
  disabled?: boolean;
}

export function SearchBar({ onSearch, disabled }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="w-full max-w-2xl mx-auto reveal mt-8">
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for a memory..."
          disabled={disabled}
          className={cn(
            "w-full bg-white border border-clay rounded-3xl pl-6 pr-16 py-5 text-lg focus:outline-none focus:border-accent transition-all shadow-sm",
            "placeholder:text-ink/30",
            disabled && "opacity-50"
          )}
        />
        <button 
          type="submit"
          className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-ink text-canvas rounded-full flex items-center justify-center transition-transform active:scale-90"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
          </svg>
        </button>
      </form>
    </div>
  );
}
