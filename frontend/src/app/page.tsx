"use client";

import  { useState, useEffect } from "react";
import { VideoLink } from "@/components/video-link";
import { SearchBar } from "@/components/search-bar";
import { ResultsGrid } from "@/components/results-grid";
import { VideoPlayer } from "@/components/video-player";
import { SiteHeader } from "@/components/site-header";
import { StatusCard } from "@/components/status-card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [videoId, setVideoId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLinking, setIsLinking] = useState(false);
  const [seekTime, setSeekTime] = useState<number | null>(null);

  useEffect(() => {
    if (!videoId || status === "completed" || status?.startsWith("error")) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/status/${videoId}`);
        const data = await res.json();
        setStatus(data.status);
      } catch (e) {
        console.error("Status polling failed", e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [videoId, status]);

  const handleLink = async (path: string) => {
    setIsLinking(true);
    try {
      const res = await fetch(`${API_BASE}/link`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path }),
      });
      const data = await res.json();
      if (res.ok) {
        setVideoId(data.video_id);
        setStatus("linked");
        await fetch(`${API_BASE}/process/${data.video_id}`, { method: "POST" });
        setStatus("processing");
      }
    } finally { setIsLinking(false); }
  };

  const handleSearch = async (q: string) => {
    setIsSearching(true);
    try {
      const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setResults(data.results);
    } finally { setIsSearching(false); }
  };

  return (
    <main className="min-h-screen px-6 py-24 sm:px-12 lg:px-24 max-w-7xl mx-auto">
      <SiteHeader />
      <div className="space-y-12">
        {!videoId ? (
          <VideoLink onLink={handleLink} isLoading={isLinking} />
        ) : (
          <>
            <StatusCard status={status} videoId={videoId} onReset={() => setVideoId(null)} />
            {videoId && status === "completed" && <VideoPlayer videoId={videoId} timestamp={seekTime} />}
          </>
        )}
        {videoId && status === "completed" && (
          <div className="space-y-12">
            <SearchBar onSearch={handleSearch} disabled={isSearching} />
            <ResultsGrid results={results} onResultClick={setSeekTime} isLoading={isSearching} />
          </div>
        )}
      </div>
    </main>
  );
}
