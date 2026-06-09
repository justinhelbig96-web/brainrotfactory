'use client';

import { useState, useEffect } from 'react';
import { Sparkles, Music, Volume2, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { createVideo, fetchVoices } from '@/lib/api';
import type { VideoRequest, Voice, Duration, Category, SubtitleStyle, Job } from '@/lib/types';

const CATEGORIES: Category[] = [
  'Horror', 'Mystery', 'Lustig', 'Verrückt',
  'Reddit Stories', 'Minecraft Stories', 'GTA Stories',
];

const DURATIONS: { value: Duration; label: string }[] = [
  { value: 30, label: '30s' },
  { value: 60, label: '60s' },
  { value: 90, label: '90s' },
];

const SUBTITLE_STYLES: { value: SubtitleStyle; label: string; desc: string }[] = [
  { value: 'tiktok',   label: 'TikTok',   desc: 'Fett, Weiß, Schwarzer Rand' },
  { value: 'fire',     label: '🔥 Fire',  desc: 'Gelb, Impact, Roter Rand' },
  { value: 'minimal',  label: 'Minimal',  desc: 'Schlicht, halbtransparent' },
];

interface Props {
  onJobCreated: (job: Job) => void;
}

export default function VideoCreator({ onJobCreated }: Props) {
  const [idea, setIdea] = useState('');
  const [duration, setDuration] = useState<Duration>(60);
  const [category, setCategory] = useState<Category>('Mystery');
  const [subtitleStyle, setSubtitleStyle] = useState<SubtitleStyle>('tiktok');
  const [voiceId, setVoiceId] = useState<string>('');
  const [includeMusic, setIncludeMusic] = useState(true);
  const [includeSfx, setIncludeSfx] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [voices, setVoices] = useState<Voice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVoices()
      .then(setVoices)
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!idea.trim()) return;

    setLoading(true);
    setError(null);

    const request: VideoRequest = {
      idea: idea.trim(),
      duration,
      category,
      voice_id: voiceId || undefined,
      subtitle_style: subtitleStyle,
      include_music: includeMusic,
      include_sfx: includeSfx,
    };

    try {
      const { job_id } = await createVideo(request);
      const newJob: Job = {
        job_id,
        status: 'queued',
        progress: 0,
        step: 'Wird vorbereitet...',
        output_file: null,
        error: null,
        idea: idea.trim(),
        category,
        duration,
      };
      onJobCreated(newJob);
      setIdea('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unbekannter Fehler';
      setError(`Fehler beim Starten: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-6 space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-white">Neue Video-Idee</h2>
        <p className="text-slate-400 text-sm mt-1">
          Gib eine Idee ein — KI schreibt die Story, generiert die Stimme und rendert das Video.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Idea input */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Deine Idee
          </label>
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder='z.B. "Ein Junge findet ein verfluchtes iPhone im Wald"'
            rows={3}
            className="w-full bg-[#0d0d18] border border-[#2a2a3e] rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-[#ff2aac] resize-none transition-colors text-sm"
            disabled={loading}
          />
          <p className="text-xs text-slate-600 mt-1.5">{idea.length} Zeichen</p>
        </div>

        {/* Duration + Category row */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Dauer</label>
            <div className="flex gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => setDuration(d.value)}
                  disabled={loading}
                  className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all border ${
                    duration === d.value
                      ? 'border-[#ff2aac] text-[#ff2aac] bg-[#ff2aac]/10'
                      : 'border-[#2a2a3e] text-slate-400 hover:border-[#3a3a5e]'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Kategorie</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as Category)}
              disabled={loading}
              className="w-full bg-[#0d0d18] border border-[#2a2a3e] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#ff2aac] transition-colors"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Music + SFX toggles */}
        <div className="flex gap-4">
          <Toggle
            id="music"
            icon={<Music className="w-4 h-4" />}
            label="Hintergrundmusik"
            checked={includeMusic}
            onChange={setIncludeMusic}
            disabled={loading}
          />
          <Toggle
            id="sfx"
            icon={<Volume2 className="w-4 h-4" />}
            label="Soundeffekte"
            checked={includeSfx}
            onChange={setIncludeSfx}
            disabled={loading}
          />
        </div>

        {/* Advanced settings */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced((v) => !v)}
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            Erweiterte Einstellungen
          </button>

          {showAdvanced && (
            <div className="mt-4 grid grid-cols-2 gap-4 border border-[#1e1e2e] rounded-xl p-4">
              {/* Voice selector */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Stimme</label>
                <select
                  value={voiceId}
                  onChange={(e) => setVoiceId(e.target.value)}
                  disabled={loading}
                  className="w-full bg-[#0d0d18] border border-[#2a2a3e] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#ff2aac] transition-colors"
                >
                  <option value="">Standard</option>
                  {voices.map((v) => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>

              {/* Subtitle style */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Untertitel-Stil</label>
                <div className="space-y-1.5">
                  {SUBTITLE_STYLES.map((s) => (
                    <button
                      key={s.value}
                      type="button"
                      onClick={() => setSubtitleStyle(s.value)}
                      disabled={loading}
                      className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all border ${
                        subtitleStyle === s.value
                          ? 'border-[#7c3aed] text-[#c084fc] bg-[#7c3aed]/10'
                          : 'border-[#2a2a3e] text-slate-400 hover:border-[#3a3a5e]'
                      }`}
                    >
                      <span className="font-semibold">{s.label}</span>
                      <span className="text-slate-500 ml-2">{s.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !idea.trim()}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Video wird erstellt...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Video erstellen
            </>
          )}
        </button>
      </form>
    </div>
  );
}

// ── Toggle component ──────────────────────────────────────────────────────

interface ToggleProps {
  id: string;
  icon: React.ReactNode;
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
}

function Toggle({ id, icon, label, checked, onChange, disabled }: ToggleProps) {
  return (
    <button
      type="button"
      id={id}
      onClick={() => onChange(!checked)}
      disabled={disabled}
      className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
        checked
          ? 'border-[#ff2aac] text-[#ff2aac] bg-[#ff2aac]/10'
          : 'border-[#2a2a3e] text-slate-500 hover:border-[#3a3a5e]'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      {icon}
      {label}
      <span className={`w-7 h-4 rounded-full transition-colors relative flex-shrink-0 ${
        checked ? 'bg-[#ff2aac]' : 'bg-[#2a2a3e]'
      }`}>
        <span className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${
          checked ? 'left-3.5' : 'left-0.5'
        }`} />
      </span>
    </button>
  );
}
