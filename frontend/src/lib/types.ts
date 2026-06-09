// Shared TypeScript types between components and API layer

export type Duration = 30 | 60 | 90;

export type Category =
  | 'Horror'
  | 'Mystery'
  | 'Lustig'
  | 'Verrückt'
  | 'Reddit Stories'
  | 'Minecraft Stories'
  | 'GTA Stories';

export type SubtitleStyle = 'tiktok' | 'minimal' | 'fire';

export type JobStatus = 'queued' | 'processing' | 'done' | 'error';

export interface VideoRequest {
  idea: string;
  duration: Duration;
  category: Category;
  voice_id?: string;
  subtitle_style: SubtitleStyle;
  include_music: boolean;
  include_sfx: boolean;
}

export interface Job {
  job_id: string;
  status: JobStatus;
  progress: number;
  step: string;
  output_file: string | null;
  error: string | null;
  idea: string;
  category: string;
  duration: number;
}

export interface Voice {
  id: string;
  name: string;
  provider: string;
}

export interface Background {
  name: string;
  path: string;
  size_mb: number;
}

export interface HealthStatus {
  status: string;
  ffmpeg: boolean;
  backgrounds: number;
}
