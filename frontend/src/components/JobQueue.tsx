'use client';

import { useEffect, useRef } from 'react';
import { CheckCircle, XCircle, Clock, Zap, Loader2, Download, Trash2 } from 'lucide-react';
import { fetchJob, deleteJob, getVideoUrl } from '@/lib/api';
import type { Job } from '@/lib/types';

const STEPS = [
  { key: 'story',    label: 'Story',     icon: '✍️' },
  { key: 'voice',    label: 'Stimme',    icon: '🎙️' },
  { key: 'subtitle', label: 'Untertitel', icon: '💬' },
  { key: 'render',   label: 'Render',    icon: '🎬' },
  { key: 'export',   label: 'Export',    icon: '📦' },
];

function getActiveStep(progress: number): number {
  if (progress < 20)  return 0;
  if (progress < 38)  return 1;
  if (progress < 58)  return 2;
  if (progress < 94)  return 3;
  return 4;
}

interface Props {
  jobs: Job[];
  onJobUpdated: (job: Job) => void;
  onJobRemoved: (jobId: string) => void;
}

export default function JobQueue({ jobs, onJobUpdated, onJobRemoved }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-white">
        Video-Queue
        <span className="ml-2 text-sm font-normal text-slate-500">
          ({jobs.length} Job{jobs.length !== 1 ? 's' : ''})
        </span>
      </h2>
      {jobs.map((job) => (
        <JobCard
          key={job.job_id}
          job={job}
          onUpdated={onJobUpdated}
          onRemoved={onJobRemoved}
        />
      ))}
    </div>
  );
}

// ── Single job card ───────────────────────────────────────────────────────

interface CardProps {
  job: Job;
  onUpdated: (job: Job) => void;
  onRemoved: (id: string) => void;
}

function JobCard({ job, onUpdated, onRemoved }: CardProps) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Poll backend while job is active
  useEffect(() => {
    if (job.status === 'done' || job.status === 'error') {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    intervalRef.current = setInterval(async () => {
      try {
        const updated = await fetchJob(job.job_id);
        onUpdated(updated);
        if (updated.status === 'done' || updated.status === 'error') {
          clearInterval(intervalRef.current!);
        }
      } catch {
        // Backend temporarily unreachable — keep polling
      }
    }, 1500);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [job.status, job.job_id, onUpdated]);

  const handleDelete = async () => {
    try {
      await deleteJob(job.job_id);
    } catch {
      // OK if already gone
    }
    onRemoved(job.job_id);
  };

  const activeStep = getActiveStep(job.progress);
  const isActive = job.status === 'queued' || job.status === 'processing';

  return (
    <div className="card p-5 space-y-4">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-white font-semibold text-sm truncate">{job.idea}</p>
          <p className="text-slate-500 text-xs mt-0.5">{job.category} · {job.duration}s</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <StatusBadge status={job.status} />
          <button
            onClick={handleDelete}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-950/40 transition-colors"
            title="Job entfernen"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Progress bar (active jobs) */}
      {isActive && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Loader2 className="w-3 h-3 animate-spin" />
              {job.step}
            </span>
            <span>{job.progress}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${job.progress}%` }} />
          </div>

          {/* Step indicators */}
          <div className="flex items-center justify-between mt-1">
            {STEPS.map((step, i) => {
              const done = i < activeStep || job.status === 'done';
              const active = i === activeStep && isActive;
              return (
                <div key={step.key} className="flex flex-col items-center gap-1">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm transition-all ${
                    done   ? 'bg-emerald-500/20 text-emerald-400' :
                    active ? 'bg-[#7c3aed]/20 text-[#c084fc] ring-1 ring-[#7c3aed]' :
                             'bg-[#1e1e2e] text-slate-600'
                  }`}>
                    {done ? <CheckCircle className="w-3.5 h-3.5" /> : step.icon}
                  </div>
                  <span className={`text-[10px] ${active ? 'text-[#c084fc]' : done ? 'text-emerald-500' : 'text-slate-600'}`}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Done: download button */}
      {job.status === 'done' && job.output_file && (
        <div className="flex items-center gap-3">
          <a
            href={getVideoUrl(job.output_file)}
            download={job.output_file}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white transition-all"
            style={{ background: 'linear-gradient(135deg, #ff2aac, #7c3aed)' }}
          >
            <Download className="w-4 h-4" />
            Video herunterladen
          </a>
          <span className="text-xs text-slate-500">{job.output_file}</span>
        </div>
      )}

      {/* Error */}
      {job.status === 'error' && job.error && (
        <div className="rounded-xl border border-red-800 bg-red-950/30 px-4 py-3">
          <p className="text-red-400 text-xs font-medium flex items-center gap-1.5">
            <XCircle className="w-3.5 h-3.5 flex-shrink-0" />
            {job.error}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Status badge ──────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: Job['status'] }) {
  const cfg = {
    queued:     { label: 'Wartend',    icon: <Clock className="w-3 h-3" />,       cls: 'badge-queued' },
    processing: { label: 'Läuft...',   icon: <Zap className="w-3 h-3" />,         cls: 'badge-processing' },
    done:       { label: 'Fertig',     icon: <CheckCircle className="w-3 h-3" />,  cls: 'badge-done' },
    error:      { label: 'Fehler',     icon: <XCircle className="w-3 h-3" />,      cls: 'badge-error' },
  }[status];

  return (
    <span className={`${cfg.cls} flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold`}>
      {cfg.icon}
      {cfg.label}
    </span>
  );
}
