import axios from 'axios';
import type { VideoRequest, Job, Voice, Background, HealthStatus } from './types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30_000,
});

export async function checkHealth(): Promise<HealthStatus> {
  const { data } = await api.get<HealthStatus>('/health');
  return data;
}

export async function fetchVoices(): Promise<Voice[]> {
  const { data } = await api.get<Voice[]>('/voices');
  return data;
}

export async function fetchBackgrounds(): Promise<Background[]> {
  const { data } = await api.get<Background[]>('/backgrounds');
  return data;
}

export async function createVideo(request: VideoRequest): Promise<{ job_id: string }> {
  const { data } = await api.post<{ job_id: string }>('/generate', request);
  return data;
}

export async function fetchJob(jobId: string): Promise<Job> {
  const { data } = await api.get<Job>(`/job/${jobId}`);
  return data;
}

export async function fetchAllJobs(): Promise<Job[]> {
  const { data } = await api.get<Job[]>('/jobs');
  return data;
}

export async function deleteJob(jobId: string): Promise<void> {
  await api.delete(`/job/${jobId}`);
}

export function getVideoUrl(filename: string): string {
  return `/api/output/${filename}`;
}
