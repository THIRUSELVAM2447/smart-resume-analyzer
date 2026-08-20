import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { analysisService } from '../services/analysisService'
import { jobService } from '../services/jobService'
import { resumeService } from '../services/resumeService'
import type { ApiError } from '../types/api'
import type { Job } from '../types/job'
import type { Resume, ResumeDetail, ResumeVersion } from '../types/resume'

const friendlyError = (error: unknown, fallback: string) => {
  const apiError = error as ApiError
  if (typeof apiError?.status !== 'number') return 'Unable to reach ResumeIQ. Confirm the backend is running and try again.'
  if (apiError.status === 401) return 'Your session has expired. Please log in again.'
  if (apiError.status === 413) return 'That PDF is larger than the allowed upload size.'
  if (apiError.status === 422) return apiError.message || 'The resume could not be processed. Ensure the PDF contains selectable text.'
  return apiError.message || fallback
}

const asItems = (value: unknown): string[] => Array.isArray(value)
  ? value.map((item) => typeof item === 'string' ? item : JSON.stringify(item)).filter(Boolean)
  : []

const getLatestVersion = (resume: ResumeDetail): ResumeVersion | null =>
  resume.versions.length
    ? [...resume.versions].sort((a, b) => b.version_number - a.version_number)[0]
    : null

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedResume, setSelectedResume] = useState<ResumeDetail | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [analysing, setAnalysing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [jobForm, setJobForm] = useState({ title: '', company_name: '', source_url: '', description: '', source_type: 'manual' })

  const latestVersion = useMemo<ResumeVersion | null>(() => {
    return selectedResume ? getLatestVersion(selectedResume) : null
  }, [selectedResume])

  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [resumeData, jobData] = await Promise.all([resumeService.getResumes(), jobService.getJobs()])
      setResumes(resumeData)
      setJobs(jobData)
      if (resumeData.length) {
        const details = await Promise.all(resumeData.map((resume) => resumeService.getResume(resume.id)))
        const selected = details
          .map((resume) => ({ resume, version: getLatestVersion(resume) }))
          .filter((entry): entry is { resume: ResumeDetail; version: ResumeVersion } => entry.version !== null)
          .sort((a, b) => new Date(b.version.created_at).getTime() - new Date(a.version.created_at).getTime())[0]?.resume
          ?? details.find((resume) => resume.is_active)
          ?? details[0]
        setSelectedResume(selected)
      }
    } catch (err) {
      setError(friendlyError(err, 'Unable to load your ResumeIQ workspace.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const loadTimer = window.setTimeout(() => { void loadData() }, 0)
    return () => window.clearTimeout(loadTimer)
  }, [])

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const chosen = event.target.files?.[0] ?? null
    setError(null)
    setNotice(null)
    if (chosen && (chosen.type !== 'application/pdf' || !chosen.name.toLowerCase().endsWith('.pdf'))) {
      setFile(null)
      setError('Please choose a PDF resume.')
      return
    }
    setFile(chosen)
  }

  async function uploadAndProcess() {
    if (!file) { setError('Choose a PDF resume before uploading.'); return }
    setUploading(true); setError(null); setNotice(null)
    try {
      const resume = await resumeService.uploadResume(file)
      const version = await resumeService.processResume(resume.id)
      const detail: ResumeDetail = { ...resume, versions: [version] }
      setResumes((current) => [resume, ...current])
      setSelectedResume(detail)
      setFile(null)
      setNotice('Resume uploaded and processed. Add a job description to see your ATS match.')
    } catch (err) {
      setError(friendlyError(err, 'Unable to upload and process this resume.'))
    } finally { setUploading(false) }
  }

  async function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!latestVersion) { setError('Upload and process a resume before starting an ATS analysis.'); return }
    if (!jobForm.description.trim()) { setError('Paste the job description before analyzing.'); return }
    setAnalysing(true); setError(null); setNotice(null)
    try {
      const job = await jobService.createJob({
        title: jobForm.title.trim() || undefined,
        company_name: jobForm.company_name.trim() || undefined,
        source_url: jobForm.source_url.trim() || undefined,
        description: jobForm.description.trim(),
        source_type: jobForm.source_type,
      })
      const analysis = await analysisService.analyzeJob(job.id, latestVersion.id)
      setJobs((current) => [job, ...current])
      navigate(`/analysis/${analysis.id}`)
    } catch (err) {
      setError(friendlyError(err, 'Unable to analyze this job right now.'))
    } finally { setAnalysing(false) }
  }

  return <main className="workspace"><header className="app-header"><div className="container app-header-inner"><button className="brand-button" onClick={() => navigate('/dashboard')}>ResumeIQ</button><div className="account"><button className="text-button" onClick={() => navigate('/portfolio')}>Portfolio</button><span>{user?.full_name}</span><button className="text-button" onClick={() => { logout(); navigate('/login') }}>Log out</button></div></div></header>
    <div className="container workspace-content">
      <section className="workspace-intro"><p className="eyebrow">Career workspace</p><h1>Welcome back, {user?.full_name?.split(' ')[0] ?? 'there'}.</h1><p>Upload a resume, paste a job description, and get a real ATS match in one guided flow.</p></section>
      {error && <p className="alert alert-error" role="alert">{error}</p>}
      {notice && <p className="alert alert-success" role="status">{notice}</p>}
      {loading ? <p className="loading">Loading your workspace…</p> : <div className="workflow-grid">
        <section className="panel"><div className="panel-heading"><div><p className="step-label">Step 1</p><h2>Your resume</h2></div>{latestVersion && <span className="status-badge">Processed</span>}</div>
          <label className="upload-zone"><input type="file" accept="application/pdf,.pdf" onChange={onFileChange} disabled={uploading} /><strong>{file ? file.name : 'Choose a PDF resume'}</strong><span>{file ? 'Ready to upload and process' : 'PDF only — it will be parsed automatically.'}</span></label>
          <button className="primary-button" onClick={uploadAndProcess} disabled={!file || uploading}>{uploading ? 'Uploading and processing…' : 'Upload & process resume'}</button>
          {selectedResume && <div className="resume-preview"><div><strong>{selectedResume.original_filename}</strong><span>{latestVersion ? `Version ${latestVersion.version_number} · parsed ${new Date(latestVersion.created_at).toLocaleDateString()}` : 'Processing needed'}</span></div>{latestVersion && <p>{latestVersion.full_name || 'Parsed resume'}{latestVersion.email ? ` · ${latestVersion.email}` : ''}</p>}</div>}
          {resumes.length > 1 && <label className="select-label">Switch resume<select value={selectedResume?.id ?? ''} onChange={async (e) => { try { setSelectedResume(await resumeService.getResume(Number(e.target.value))) } catch (err) { setError(friendlyError(err, 'Unable to load that resume.')) } }}>{resumes.map((resume) => <option key={resume.id} value={resume.id}>{resume.original_filename}</option>)}</select></label>}
        </section>
        <section className="panel"><div className="panel-heading"><div><p className="step-label">Step 2</p><h2>Target opportunity</h2></div></div>
          <form onSubmit={handleAnalyze} className="job-form"><div className="form-row"><label>Job title<input value={jobForm.title} onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })} placeholder="e.g. Software Engineer" /></label><label>Company <span className="optional">optional</span><input value={jobForm.company_name} onChange={(e) => setJobForm({ ...jobForm, company_name: e.target.value })} placeholder="Company name" /></label></div><div className="form-row"><label>Source URL <span className="optional">optional</span><input type="url" value={jobForm.source_url} onChange={(e) => setJobForm({ ...jobForm, source_url: e.target.value })} placeholder="https://…" /></label><label>Source<select value={jobForm.source_type} onChange={(e) => setJobForm({ ...jobForm, source_type: e.target.value })}><option value="manual">Manual</option><option value="linkedin">LinkedIn</option><option value="company">Company site</option><option value="referral">Referral</option></select></label></div><label>Job description<textarea required value={jobForm.description} onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })} placeholder="Paste the complete job description here…" rows={8} /></label><button className="primary-button" type="submit" disabled={!latestVersion || analysing}>{analysing ? 'Creating your ATS analysis…' : latestVersion ? 'Analyze my match' : 'Process a resume first'}</button></form>
        </section>
      </div>}
      {latestVersion && <section className="panel parsed-panel"><div className="panel-heading"><div><p className="step-label">Parsed resume</p><h2>{latestVersion.full_name || selectedResume?.original_filename}</h2></div></div><div className="parsed-details">{latestVersion.email && <span>{latestVersion.email}</span>}{latestVersion.phone && <span>{latestVersion.phone}</span>}{latestVersion.location && <span>{latestVersion.location}</span>}</div>{latestVersion.summary && <p className="parsed-summary">{latestVersion.summary}</p>}{asItems(latestVersion.skills).length > 0 && <div className="tag-list parsed-skills">{asItems(latestVersion.skills).map((skill) => <span key={skill}>{skill}</span>)}</div>}<div className="parsed-sections">{(['experience', 'education', 'projects', 'certifications', 'achievements'] as const).map((section) => { const items = asItems(latestVersion[section]); return items.length ? <div key={section}><h3>{section}</h3><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></div> : null })}</div></section>}
      {!loading && <section className="panel recent-panel"><div className="panel-heading"><div><p className="step-label">Saved opportunities</p><h2>Recent jobs</h2></div></div>{jobs.length ? <ul className="recent-list">{jobs.slice(0, 5).map((job) => <li key={job.id}><div><strong>{job.title || 'Untitled opportunity'}</strong><span>{job.company_name || 'Company not specified'} · {new Date(job.created_at).toLocaleDateString()}</span></div><button className="text-button" onClick={async () => { try { const analyses = await analysisService.getJobAnalyses(job.id); if (analyses[0]) navigate(`/analysis/${analyses[0].id}`); else setNotice('This job has not been analyzed yet.') } catch (err) { setError(friendlyError(err, 'Unable to load this analysis.')) } }}>View result</button></li>)}</ul> : <p className="empty-copy">Your saved opportunities and analysis history will appear here.</p>}</section>}
      <section className="profile-panel"><h2>Professional portfolio</h2><p>{latestVersion ? 'Generate and manage a professional profile directly from your latest processed resume.' : 'Process a resume to generate a professional profile without re-entering your details.'}</p><div className="profile-details">{latestVersion && <><span>{latestVersion.location || 'Location not detected'}</span><span>{asItems(latestVersion.skills).slice(0, 6).join(' · ') || 'Skills will appear after parsing'}</span></>}</div><button className="text-button portfolio-link" onClick={() => navigate('/portfolio')}>Open portfolio</button></section>
    </div></main>
}
