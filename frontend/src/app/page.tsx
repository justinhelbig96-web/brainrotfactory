'use client';

import { useState, useEffect } from 'react';
import { Clapperboard, Wifi, WifiOff, FolderVideo } from 'lucide-react';
import VideoCreator from '@/components/VideoCreator';
import JobQueue from '@/components/JobQueue';
import { checkHealth } from '@/lib/api';
import type { HealthStatus, Job } from '@/lib/types';

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthError, setHealthError] = useState(false);
  const [activeJobs, setActiveJobs] = useState<Job[]>([]);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealthError(true));
  }, []);

  const handleJobCreated = (job: Job) => {
    setActiveJobs((prev) => [job, ...prev]);
  };

  const handleJobUpdated = (updated: Job) => {
    setActiveJobs((prev) =>
      prev.map((j) => (j.job_id === updated.job_id ? updated : j))
    );
  };

  const handleJobRemoved = (jobId: string) => {
    setActiveJobs((prev) => prev.filter((j) => j.job_id !== jobId));
  };

  return (
    <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* ── Header ── */}
      <header className="border-b border-[#1e1e2e] sticky top-0 z-50 backdrop-blur-md bg-[rgba(10,10,15,0.85)]">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, #ff2aac, #7c3aed)' }}>
              <Clapperboard className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">
                Brainrot Video Factory
              </h1>
              <p className="text-xs text-slate-500">TikTok Videos auf Knopfdruck</p>
            </div>
          </div>

          {/* Health indicators */}
          <div className="flex items-center gap-3 text-xs">
            {healthError ? (
              <span className="flex items-center gap-1.5 text-red-400">
                <WifiOff className="w-3.5 h-3.5" />
                Backend offline
              </span>
            ) : health ? (
              <>
                <span className={`flex items-center gap-1.5 ${health.ffmpeg ? 'text-emerald-400' : 'text-red-400'}`}>
                  <span className={`w-2 h-2 rounded-full ${health.ffmpeg ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  FFmpeg {health.ffmpeg ? 'OK' : 'fehlt'}
                </span>
                <span className="flex items-center gap-1.5 text-slate-400">
                  <FolderVideo className="w-3.5 h-3.5" />
                  {health.backgrounds} Clip{health.backgrounds !== 1 ? 's' : ''}
                </span>
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <Wifi className="w-3.5 h-3.5" />
                  Online
                </span>
              </>
            ) : (
              <span className="text-slate-500 animate-pulse">Verbinde...</span>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">

        {/* FFmpeg warning */}
        {health && !health.ffmpeg && (
          <div className="rounded-xl border border-red-800 bg-red-950/40 px-5 py-4 text-sm text-red-300">
            <strong>⚠ FFmpeg nicht gefunden.</strong> Bitte FFmpeg installieren und zum PATH hinzufügen.{' '}
            <a href="https://ffmpeg.org/download.html" target="_blank" rel="noopener noreferrer"
               className="underline hover:text-red-100">ffmpeg.org/download.html</a>
          </div>
        )}

        {/* No backgrounds warning */}
        {health && health.backgrounds === 0 && (
          <div className="rounded-xl border border-yellow-800 bg-yellow-950/40 px-5 py-4 text-sm text-yellow-300">
            <strong>⚠ Keine Hintergrundvideos gefunden.</strong>{' '}
            Lege eigene MP4-Clips (z.B. Minecraft Parkour, Subway Surfers) in den Ordner{' '}
            <code className="bg-yellow-900/50 px-1.5 py-0.5 rounded text-yellow-200">assets/backgrounds/</code>
          </div>
        )}

        {/* Creator form */}
        <VideoCreator onJobCreated={handleJobCreated} />

        {/* Job queue */}
        {activeJobs.length > 0 && (
          <JobQueue
            jobs={activeJobs}
            onJobUpdated={handleJobUpdated}
            onJobRemoved={handleJobRemoved}
          />
        )}
      </div>
    </main>
  );
}
