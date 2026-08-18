import { useNavigate } from 'react-router-dom'
import '../App.css'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <>
      <header className="site-header">
        <div className="container header-inner">
          <span className="brand">ResumeIQ</span>
          <nav className="main-nav" aria-label="Primary navigation">
            <ul>
              <li>Dashboard</li>
              <li>Resumes</li>
              <li>Jobs</li>
              <li>Portfolio</li>
            </ul>
          </nav>
          <div className="profile-placeholder" aria-hidden="true">
            <span>P</span>
          </div>
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
              onClick={() => navigate('/register')}
            >
              Get Started
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