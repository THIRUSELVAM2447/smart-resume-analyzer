import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { portfolioService } from '../services/portfolioService'
import { resumeService } from '../services/resumeService'
import type { ApiError } from '../types/api'
import type { Portfolio as PortfolioData } from '../types/portfolio'
import type { ResumeDetail, ResumeVersion } from '../types/resume'

const newestVersion = (resumes: ResumeDetail[]) => resumes.flatMap((resume) => resume.versions).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0] ?? null
const items = (value: string[] | null) => value?.filter(Boolean) ?? []
const errorMessage = (error: unknown, fallback: string) => { const apiError = error as ApiError; return typeof apiError?.status === 'number' ? apiError.message || fallback : 'Unable to reach ResumeIQ. Confirm the backend is running and try again.' }

function PortfolioPreview({ portfolio }: { portfolio: PortfolioData }) {
  const sections: Array<[string, string[] | null]> = [['Experience', portfolio.experience], ['Education', portfolio.education], ['Projects', portfolio.projects], ['Certifications', portfolio.certifications], ['Achievements', portfolio.achievements]]
  return <section className="portfolio-preview"><div className="portfolio-identity"><h2>{portfolio.headline || 'Professional portfolio'}</h2>{portfolio.bio && <p>{portfolio.bio}</p>}<div className="parsed-details">{portfolio.email && <span>{portfolio.email}</span>}{portfolio.phone && <span>{portfolio.phone}</span>}{portfolio.location && <span>{portfolio.location}</span>}{portfolio.linkedin_url && <a href={portfolio.linkedin_url} target="_blank" rel="noreferrer">LinkedIn</a>}{portfolio.github_url && <a href={portfolio.github_url} target="_blank" rel="noreferrer">GitHub</a>}</div></div>{items(portfolio.skills).length > 0 && <section><h3>Skills</h3><div className="tag-list parsed-skills">{items(portfolio.skills).map((skill) => <span key={skill}>{skill}</span>)}</div></section>}{sections.map(([title, sectionItems]) => items(sectionItems).length ? <section key={title}><h3>{title}</h3><ul>{items(sectionItems).map((item) => <li key={item}>{item}</li>)}</ul></section> : null)}</section>
}

export default function Portfolio() {
  const navigate = useNavigate()
  const [details, setDetails] = useState<ResumeDetail[]>([])
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null)
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null)
  const [headline, setHeadline] = useState('')
  const [bio, setBio] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [location, setLocation] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const latest = useMemo<ResumeVersion | null>(() => details.flatMap((resume) => resume.versions).find((version) => version.id === selectedVersionId) ?? newestVersion(details), [details, selectedVersionId])

  function applyPortfolio(data: PortfolioData) {
    setPortfolio(data)
    setHeadline(data.headline ?? '')
    setBio(data.bio ?? '')
    setEmail(data.email ?? '')
    setPhone(data.phone ?? '')
    setLocation(data.location ?? '')
    setLinkedinUrl(data.linkedin_url ?? '')
    setGithubUrl(data.github_url ?? '')
    setIsPublished(data.is_published)
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void (async () => {
        try {
          const resumeList = await resumeService.getResumes()
          const resumeDetails = await Promise.all(resumeList.map((resume) => resumeService.getResume(resume.id)))
          setDetails(resumeDetails)
          setSelectedVersionId(newestVersion(resumeDetails)?.id ?? null)
          try {
            applyPortfolio(await portfolioService.getMyPortfolio())
          } catch (err) {
            if ((err as ApiError).status !== 404) setError(errorMessage(err, 'Unable to load your portfolio.'))
          }
        } catch (err) {
          setError(errorMessage(err, 'Unable to load your processed resumes.'))
        } finally {
          setLoading(false)
        }
      })()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [])

  async function generate() {
    if (!latest) { setError('Process a resume before generating a portfolio.'); return }
    setGenerating(true); setError(null); setNotice(null)
    try {
      applyPortfolio(await portfolioService.generate(latest.id))
      setNotice('Your portfolio was generated from the selected resume version.')
    } catch (err) {
      setError(errorMessage(err, 'Unable to generate your portfolio.'))
    } finally { setGenerating(false) }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!portfolio) return
    setSaving(true); setError(null); setNotice(null)
    try {
      applyPortfolio(await portfolioService.update(portfolio.id, {
        headline: headline.trim() || null,
        bio: bio.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        location: location.trim() || null,
        linkedin_url: linkedinUrl.trim() || null,
        github_url: githubUrl.trim() || null,
        is_published: isPublished,
      }))
      setNotice('Portfolio changes saved.')
    } catch (err) {
      setError(errorMessage(err, 'Unable to save your portfolio.'))
    } finally { setSaving(false) }
  }

  const versions = details.flatMap((resume) => resume.versions).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  const resumeName = (resumeId: number) => details.find((resume) => resume.id === resumeId)?.original_filename

  return (
    <main className="workspace">
      <header className="app-header">
        <div className="container app-header-inner">
          <button className="brand-button" onClick={() => navigate('/dashboard')}>ResumeIQ</button>
          <button className="text-button" onClick={() => navigate('/dashboard')}>Back to dashboard</button>
        </div>
      </header>
      <div className="container workspace-content">
        <section className="workspace-intro">
          <p className="eyebrow">Professional profile</p>
          <h1>Your resume-derived portfolio</h1>
          <p>Generate a polished profile from a processed resume, then edit only its presentation details.</p>
        </section>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        {notice && <p className="alert alert-success" role="status">{notice}</p>}
        {loading ? <p className="loading">Loading your portfolio workspace…</p> : (
          <>
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <p className="step-label">Source resume</p>
                  <h2>Generate from a processed version</h2>
                </div>
              </div>
              {versions.length ? (
                <>
                  <label className="select-label">Resume version
                    <select value={latest?.id ?? ''} onChange={(event) => setSelectedVersionId(Number(event.target.value))}>
                      {versions.map((version) => (
                        <option key={version.id} value={version.id}>
                          {resumeName(version.resume_id) || 'Resume'} · Version {version.version_number} · {new Date(version.created_at).toLocaleDateString()}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button className="primary-button portfolio-action" onClick={generate} disabled={generating}>
                    {generating ? 'Generating portfolio…' : portfolio ? 'Refresh from selected resume' : 'Generate portfolio'}
                  </button>
                </>
              ) : (
                <p className="empty-copy">Upload and process a resume from the dashboard before creating a portfolio.</p>
              )}
            </section>
            {portfolio && (
              <div className="portfolio-grid">
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="step-label">Portfolio preview</p>
                      <h2>{portfolio.is_published ? 'Published portfolio' : 'Private preview'}</h2>
                    </div>
                  </div>
                  <PortfolioPreview portfolio={portfolio} />
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="step-label">Presentation</p>
                      <h2>Edit portfolio details</h2>
                    </div>
                  </div>
                  <form className="job-form" onSubmit={save}>
                    <label>Headline<input value={headline} onChange={(event) => setHeadline(event.target.value)} placeholder="Professional headline" /></label>
                    <label>About<textarea value={bio} onChange={(event) => setBio(event.target.value)} rows={7} placeholder="Resume summary" /></label>
                    <div className="form-row">
                      <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
                      <label>Phone<input value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="Phone number" /></label>
                    </div>
                    <label>Location<input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="City, country" /></label>
                    <label>LinkedIn URL<input value={linkedinUrl} onChange={(event) => setLinkedinUrl(event.target.value)} placeholder="https://linkedin.com/in/…" /></label>
                    <label>GitHub URL<input value={githubUrl} onChange={(event) => setGithubUrl(event.target.value)} placeholder="https://github.com/…" /></label>
                    <label className="publish-toggle">
                      <input type="checkbox" checked={isPublished} onChange={(event) => setIsPublished(event.target.checked)} />
                      Publish this portfolio publicly
                    </label>
                    <button className="primary-button" type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</button>
                  </form>
                  {portfolio.is_published && (
                    <p className="public-link">
                      Public link: <a href={`/portfolio/public/${portfolio.slug}`} target="_blank" rel="noreferrer">/portfolio/public/{portfolio.slug}</a>
                    </p>
                  )}
                </section>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  )
}
