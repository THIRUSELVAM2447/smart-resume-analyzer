import { api } from './api'
import type { Portfolio, PortfolioUpdate } from '../types/portfolio'

export const portfolioService = {
  getMyPortfolio: (): Promise<Portfolio> => api.get<Portfolio>('/api/portfolios'),
  generate: (resumeVersionId: number): Promise<Portfolio> =>
    api.post<Portfolio>('/api/portfolios/generate', { resume_version_id: resumeVersionId }),
  update: (portfolioId: number, update: PortfolioUpdate): Promise<Portfolio> =>
    api.patch<Portfolio>(`/api/portfolios/${portfolioId}`, update),
  getPublic: (slug: string): Promise<Portfolio> =>
    api.get<Portfolio>(`/api/portfolios/public/${slug}`),
}
