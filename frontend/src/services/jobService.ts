import { api } from './api'
import type { Job, JobCreate } from '../types/job'

export const jobService = {
  getJobs: (): Promise<Job[]> => api.get<Job[]>('/api/jobs'),
  getJob: (jobId: number): Promise<Job> => api.get<Job>(`/api/jobs/${jobId}`),
  createJob: (job: JobCreate): Promise<Job> => api.post<Job>('/api/jobs', job),
}
