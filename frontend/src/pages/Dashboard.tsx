import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { resumeService } from '../services/resumeService'
import type { Resume } from '../types/resume'
import type { ApiError } from '../types/api'

export default function Dashboard() {
  const { user } = useAuth()

  const [resumes, setResumes] = useState<Resume[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    async function loadResumes() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await resumeService.getResumes()
        if (isMounted) {
          setResumes(data)
        }
      } catch (err) {
        const apiError = err as ApiError
        if (isMounted) {
          setError('Unable to load your resumes. Please try again.')
        }
        // apiError is intentionally unused beyond triggering the branch —
        // no technical details are shown to the user.
        void apiError
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadResumes()

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <main style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.heading}>Dashboard</h1>
        <p style={styles.welcome}>
          Welcome back, {user?.full_name ?? 'there'}.
        </p>
        <p style={styles.description}>
          ResumeIQ helps you manage your resumes, analyze job opportunities,
          and build your professional profile in one place.
        </p>

        <div style={styles.cardGrid}>
          <article style={styles.card}>
            <h2 style={styles.cardHeading}>Resume Analysis</h2>
            <p style={styles.cardText}>
              Analyze your resume and understand its strengths.
            </p>
          </article>

          <article style={styles.card}>
            <h2 style={styles.cardHeading}>Job Matching</h2>
            <p style={styles.cardText}>
              Compare your resume against job opportunities.
            </p>
          </article>

          <article style={styles.card}>
            <h2 style={styles.cardHeading}>Portfolio</h2>
            <p style={styles.cardText}>
              Build and maintain your professional profile.
            </p>
          </article>
        </div>

        <section style={styles.resumesSection}>
          <h2 style={styles.sectionHeading}>Your Resumes</h2>

          {isLoading && <p style={styles.statusText}>Loading your resumes…</p>}

          {!isLoading && error && (
            <p role="alert" style={styles.errorText}>
              {error}
            </p>
          )}

          {!isLoading && !error && resumes.length === 0 && (
            <div style={styles.emptyState}>
              <p style={styles.emptyStateTitle}>No resumes yet.</p>
              <p style={styles.emptyStateText}>
                Once resume upload is available, you'll be able to add a
                resume here.
              </p>
            </div>
          )}

          {!isLoading && !error && resumes.length > 0 && (
            <ul style={styles.resumeList}>
              {resumes.map((resume) => (
                <li key={resume.id} style={styles.resumeItem}>
                  <div style={styles.resumeItemMain}>
                    <span style={styles.resumeFilename}>
                      {resume.original_filename}
                    </span>
                    <span style={styles.resumeDate}>
                      Added {new Date(resume.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span
                    style={
                      resume.is_active
                        ? styles.statusBadgeActive
                        : styles.statusBadgeInactive
                    }
                  >
                    {resume.is_active ? 'Active' : 'Inactive'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section style={styles.getStarted}>
          <h2 style={styles.getStartedHeading}>Get started</h2>
          <p style={styles.getStartedText}>
            Upload or work on a resume to begin analyzing and improving your
            professional profile.
          </p>
        </section>
      </div>
    </main>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100svh',
    background: 'var(--color-bg)',
    padding: 'var(--space-6) var(--space-5)',
  },
  container: {
    maxWidth: '1000px',
    margin: '0 auto',
  },
  heading: {
    fontSize: '30px',
    margin: '0 0 var(--space-2)',
  },
  welcome: {
    fontSize: '16px',
    color: 'var(--color-text)',
    margin: '0 0 var(--space-2)',
  },
  description: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--color-text-secondary)',
    margin: '0 0 var(--space-7)',
    maxWidth: '640px',
  },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 'var(--space-5)',
    marginBottom: 'var(--space-7)',
  },
  card: {
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-surface)',
    padding: 'var(--space-5)',
  },
  cardHeading: {
    fontSize: '18px',
    margin: '0 0 var(--space-2)',
  },
  cardText: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--color-text-secondary)',
    margin: 0,
  },
  resumesSection: {
    marginBottom: 'var(--space-7)',
  },
  sectionHeading: {
    fontSize: '20px',
    margin: '0 0 var(--space-4)',
  },
  statusText: {
    fontSize: '14px',
    color: 'var(--color-text-secondary)',
    margin: 0,
  },
  errorText: {
    fontSize: '14px',
    color: 'var(--color-error)',
    margin: 0,
  },
  emptyState: {
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-surface)',
    padding: 'var(--space-5)',
  },
  emptyStateTitle: {
    fontSize: '15px',
    fontWeight: 600,
    color: 'var(--color-text)',
    margin: '0 0 var(--space-2)',
  },
  emptyStateText: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--color-text-secondary)',
    margin: 0,
  },
  resumeList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-3)',
  },
  resumeItem: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 'var(--space-3)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-surface)',
    padding: 'var(--space-4)',
  },
  resumeItemMain: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    minWidth: 0,
  },
  resumeFilename: {
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--color-text)',
    wordBreak: 'break-word',
  },
  resumeDate: {
    fontSize: '13px',
    color: 'var(--color-text-secondary)',
  },
  statusBadgeActive: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-success)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    padding: '4px 10px',
    flexShrink: 0,
  },
  statusBadgeInactive: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    padding: '4px 10px',
    flexShrink: 0,
  },
  getStarted: {
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-surface)',
    padding: 'var(--space-5)',
  },
  getStartedHeading: {
    fontSize: '18px',
    margin: '0 0 var(--space-2)',
  },
  getStartedText: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--color-text-secondary)',
    margin: 0,
  },
}