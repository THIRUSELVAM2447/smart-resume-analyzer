import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Landing() {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()

  return (
    <>
      <header className="site-header">
        <div className="container header-inner">
          <span className="brand">ResumeIQ</span>
          <nav className="main-nav" aria-label="Primary navigation">
            <ul>
              <li>
                <Link to={isAuthenticated ? '/dashboard' : '/login'}>Dashboard</Link>
              </li>
              <li>
                <Link to={isAuthenticated ? '/dashboard' : '/login'}>Resumes</Link>
              </li>
              <li>
                <Link to={isAuthenticated ? '/dashboard' : '/login'}>Jobs</Link>
              </li>
              <li>
                <Link to={isAuthenticated ? '/portfolio' : '/login'}>Portfolio</Link>
              </li>
            </ul>
          </nav>
          {isAuthenticated ? (
            <button type="button" className="text-button" onClick={() => navigate('/dashboard')}>
              Open workspace
            </button>
          ) : (
            <button type="button" className="text-button" onClick={() => navigate('/login')}>
              Log in
            </button>
          )}
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container hero-inner">
            <p className="eyebrow">AI-powered career tools</p>
            <h1>Build a stronger career profile</h1>
            <p className="hero-copy">
              ResumeIQ helps you understand your resume, prepare for
              opportunities, and build a stronger professional profile.
            </p>
            <button
              type="button"
              className="btn-primary"
              disabled={isLoading}
              onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
            >
              {isAuthenticated ? 'Go to dashboard' : 'Get Started'}
            </button>
          </div>
        </section>

        <section className="features" aria-label="Core capabilities">
          <div className="container features-grid">
            <article className="feature-card">
              <h2>Resume Analysis</h2>
              <p>Understand how your resume is structured and presented.</p>
            </article>
            <article className="feature-card">
              <h2>Job Matching</h2>
              <p>
                Prepare your resume for the opportunities you want to
                pursue.
              </p>
            </article>
            <article className="feature-card">
              <h2>Portfolio</h2>
              <p>
                Build a professional profile from the experience you
                already have.
              </p>
            </article>
          </div>
        </section>
      </main>
    </>
  )
}
