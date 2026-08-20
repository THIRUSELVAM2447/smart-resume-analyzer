export interface AnalysisSnapshot {
  job?: { title?: string | null; company_name?: string | null }
  resume?: { full_name?: string | null; version_number?: number }
  scores?: { keyword_score?: number; grammar_score?: number }
}

export interface JobAnalysis {
  id: number
  job_id: number
  resume_version_id: number
  overall_score: number
  skill_score: number | null
  matched_skills: string[] | null
  missing_skills: string[] | null
  extra_skills: string[] | null
  grammar_issues: string[] | null
  recommendations: string[] | null
  analysis_snapshot: AnalysisSnapshot | null
  created_at: string
}
