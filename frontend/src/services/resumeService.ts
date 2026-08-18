import { api } from './api'
import type { Resume, ResumeDetail, ResumeVersion } from '../types/resume'

export const resumeService = {
  getResumes: (): Promise<Resume[]> => {
    return api.get<Resume[]>('/api/resumes')
  },

  getResume: (resumeId: number): Promise<ResumeDetail> => {
    return api.get<ResumeDetail>(`/api/resumes/${resumeId}`)
  },

  getResumeVersion: (
    resumeId: number,
    versionNumber: number
  ): Promise<ResumeVersion> => {
    return api.get<ResumeVersion>(
      `/api/resumes/${resumeId}/versions/${versionNumber}`
    )
  },

  createResume: (originalFilename: string): Promise<Resume> => {
    return api.post<Resume>('/api/resumes', {
      original_filename: originalFilename,
    })
  },
}