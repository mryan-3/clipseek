"use client";

import React, { useRef, useEffect } from "react";

interface VideoPlayerProps {
  videoId: string;
  timestamp: number | null;
}

export function VideoPlayer({ videoId, timestamp }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && timestamp !== null) {
      videoRef.current.currentTime = timestamp;
      videoRef.current.play();
    }
  }, [timestamp]);

  return (
    <div className="w-full max-w-4xl mx-auto mb-16 reveal">
      <video
        ref={videoRef}
        controls
        className="w-full rounded-2xl border border-clay shadow-sm bg-ink/5"
        src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/video-stream/${videoId}`}
      />
    </div>
  );
}
