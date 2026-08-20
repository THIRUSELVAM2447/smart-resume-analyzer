import { api } from './api'
import type { JobAnalysis } from '../types/analysis'

export const analysisService = {
  analyzeJob: (jobId: number, resumeVersionId: number): Promise<JobAnalysis> =>
    api.post<JobAnalysis>(`/api/job-analyses/jobs/${jobId}/analyze`, {
      resume_version_id: resumeVersionId,
    }),
  getAnalysis: (analysisId: number): Promise<JobAnalysis> =>
    api.get<JobAnalysis>(`/api/job-analyses/${analysisId}`),
  getJobAnalyses: (jobId: number): Promise<JobAnalysis[]> =>
    api.get<JobAnalysis[]>(`/api/job-analyses/jobs/${jobId}`),
}
