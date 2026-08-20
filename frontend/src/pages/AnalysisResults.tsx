import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { analysisService } from '../services/analysisService'
import { jobService } from '../services/jobService'
import type { JobAnalysis } from '../types/analysis'
import type { Job } from '../types/job'

const ScoreCard = ({ label, score }: { label: string; score: number | null | undefined }) => <article className="score-card"><span>{label}</span><strong>{typeof score === 'number' ? score : '—'}<small>{typeof score === 'number' ? ' / 100' : ''}</small></strong><div className="score-track"><i style={{ width: `${Math.max(0, Math.min(score ?? 0, 100))}%` }} /></div></article>
const SkillGroup = ({ title, items, kind }: { title: string; items: string[] | null; kind: string }) => <section className={`skill-group ${kind}`}><h3>{title}</h3>{items?.length ? <div className="tag-list">{items.map((item) => <span key={item}>{item}</span>)}</div> : <p>None detected.</p>}</section>

export default function AnalysisResults() {
  const { analysisId } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState<JobAnalysis | null>(null)
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { async function load() { try { const result = await analysisService.getAnalysis(Number(analysisId)); setAnalysis(result); setJob(await jobService.getJob(result.job_id)) } catch { setError('This analysis could not be found or is no longer available.') } } if (Number(analysisId)) void load() }, [analysisId])
  if (!Number(analysisId)) return <main className="results-page"><div className="container"><p className="alert alert-error">This analysis link is invalid.</p><button className="primary-button" onClick={() => navigate('/dashboard')}>Back to dashboard</button></div></main>
  if (error) return <main className="results-page"><div className="container"><p className="alert alert-error">{error}</p><button className="primary-button" onClick={() => navigate('/dashboard')}>Back to dashboard</button></div></main>
  if (!analysis) return <main className="results-page"><div className="container loading">Loading your ATS results…</div></main>
  const scores = analysis.analysis_snapshot?.scores
  return <main className="results-page"><header className="app-header"><div className="container app-header-inner"><button className="brand-button" onClick={() => navigate('/dashboard')}>ResumeIQ</button><div className="account"><button className="text-button" onClick={() => navigate('/portfolio')}>Portfolio</button><button className="text-button" onClick={() => navigate('/dashboard')}>← Dashboard</button></div></div></header><div className="container results-content"><section className="results-hero"><p className="eyebrow">ATS results</p><h1>{job?.title || analysis.analysis_snapshot?.job?.title || 'Job match analysis'}</h1><p>{job?.company_name || analysis.analysis_snapshot?.job?.company_name || 'Target opportunity'} · Created {new Date(analysis.created_at).toLocaleDateString()}</p></section><section className="score-grid"><ScoreCard label="Overall ATS score" score={analysis.overall_score} /><ScoreCard label="Skill match" score={analysis.skill_score} /><ScoreCard label="Keyword match" score={scores?.keyword_score} /><ScoreCard label="Grammar" score={scores?.grammar_score} /></section><section className="results-grid"><div className="panel"><h2>Skills alignment</h2><SkillGroup title="Matched skills" items={analysis.matched_skills} kind="matched" /><SkillGroup title="Missing skills" items={analysis.missing_skills} kind="missing" /><SkillGroup title="Additional skills" items={analysis.extra_skills} kind="extra" /></div><div className="panel"><h2>Recommendations</h2>{analysis.recommendations?.length ? <ol className="recommendations">{analysis.recommendations.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ol> : <p className="empty-copy">No recommendations were generated for this analysis.</p>}<h2 className="grammar-heading">Grammar review</h2>{analysis.grammar_issues?.length ? <ul className="issues">{analysis.grammar_issues.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul> : <p className="grammar-good">No grammar issues detected.</p>}</div></section><section className="profile-panel"><h2>Analysis details</h2><p>Compared {analysis.analysis_snapshot?.resume?.full_name || 'your processed resume'} against this opportunity. The results use your latest selected resume version automatically.</p></section></div></main>
}
