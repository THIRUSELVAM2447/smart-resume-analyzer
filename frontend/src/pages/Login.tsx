import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { ApiError } from '../types/api'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (email.trim() === '') {
      setError('Please enter your email.')
      return
    }

    if (password === '') {
      setError('Please enter your password.')
      return
    }

    setIsSubmitting(true)

    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (err) {
      const apiError = err as ApiError

      if (apiError.status === 401) {
        setError('Incorrect email or password.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main style={styles.page}>
      <div style={styles.card}>
        <p style={styles.brand}>ResumeIQ</p>
        <h1 style={styles.heading}>Welcome back</h1>
        <p style={styles.supportingText}>
          Log in to continue working on your resumes and portfolio.
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <div style={styles.field}>
            <label htmlFor="email" style={styles.label}>
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label htmlFor="password" style={styles.label}>
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              style={styles.input}
            />
          </div>

          {error && (
            <p role="alert" style={styles.error}>
              {error}
            </p>
          )}

          <button type="submit" disabled={isSubmitting} style={styles.button}>
            {isSubmitting ? 'Logging in…' : 'Log in'}
          </button>
        </form>

        <p style={styles.footerText}>
         Don&apos;t have an account?{' '}
        <Link to="/register" style={styles.link}>
           Create one.
        </Link>
    </p>
      </div>
    </main>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100svh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'var(--color-bg)',
    padding: 'var(--space-5)',
  },
  card: {
    width: '100%',
    maxWidth: '380px',
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--space-6)',
  },
  brand: {
    fontFamily: 'var(--font-heading)',
    fontSize: '16px',
    fontWeight: 600,
    color: 'var(--color-text)',
    margin: 0,
  },
  heading: {
    fontSize: '26px',
    margin: 'var(--space-2) 0 var(--space-2)',
  },
  supportingText: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--color-text-secondary)',
    margin: '0 0 var(--space-6)',
  },
  field: {
    marginBottom: 'var(--space-4)',
  },
  label: {
    display: 'block',
    fontSize: '13px',
    fontWeight: 500,
    color: 'var(--color-text)',
    marginBottom: 'var(--space-2)',
  },
  input: {
    width: '100%',
    boxSizing: 'border-box',
    fontFamily: 'var(--font-sans)',
    fontSize: '15px',
    padding: '10px 12px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--color-border)',
    background: 'var(--color-bg)',
    color: 'var(--color-text)',
  },
  error: {
    fontSize: '13px',
    color: 'var(--color-error)',
    margin: '0 0 var(--space-4)',
  },
  button: {
    width: '100%',
    background: 'var(--color-accent)',
    color: '#ffffff',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    padding: '12px',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
  },
 footerText: {
  fontSize: '13px',
  color: 'var(--color-text-secondary)',
  textAlign: 'center',
  marginTop: 'var(--space-5)',
  marginBottom: 0,
},

link: {
  color: 'var(--color-accent)',
  textDecoration: 'none',
  fontWeight: 500,
},
}