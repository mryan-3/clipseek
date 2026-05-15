"use client";

import React, { useRef, useEffect } from "react";

interface VideoPlayerProps {
  videoId: string;
  timestamp: number | null;
}

export function VideoPlayer({ videoId, timestamp }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const video = videoRef.current;
    if (!video || timestamp === null) return;

    const handleSeek = () => {
      video.currentTime = timestamp;
      video.play().catch(e => console.error("Playback failed", e));
    };

    // If video metadata is already loaded, seek immediately
    if (video.readyState >= 1) {
      handleSeek();
    } else {
      // Otherwise wait for metadata
      video.addEventListener("loadedmetadata", handleSeek, { once: true });
    }
  }, [timestamp]);

  return (
    <div className="w-full max-w-4xl mx-auto mb-16 reveal overflow-hidden rounded-2xl border border-clay shadow-sm bg-ink/5 aspect-video">
      <video
        ref={videoRef}
        controls
        playsInline
        className="w-full h-full"
        src={`${API_URL}/video-stream/${videoId}`}
      />
    </div>
  );
}
