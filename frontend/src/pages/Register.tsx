import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../services/authService'
import type { ApiError } from '../types/api'

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function validate(): string | null {
    if (fullName.trim() === '') {
      return 'Please enter your full name.'
    }

    if (email.trim() === '') {
      return 'Please enter your email.'
    }

    if (password === '') {
      return 'Please enter a password.'
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters.'
    }

    if (confirmPassword === '') {
      return 'Please confirm your password.'
    }

    if (password !== confirmPassword) {
      return 'Passwords do not match.'
    }

    return null
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)

    try {
      await authService.register({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      })

      setSuccess('Account created successfully. You can now log in.')
      setFullName('')
      setEmail('')
      setPassword('')
      setConfirmPassword('')
    } catch (err) {
      const apiError = err as ApiError

      if (apiError.status === 409) {
        setError('This email is already registered. Please use another email.')
      } else if (apiError.status === 422) {
        setError('Please check your information and try again.')
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
        <h1 style={styles.heading}>Create your account</h1>
        <p style={styles.supportingText}>
          Sign up to start analyzing your resume and building your
          portfolio.
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <div style={styles.field}>
            <label htmlFor="fullName" style={styles.label}>
              Full name
            </label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              autoComplete="name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              style={styles.input}
            />
          </div>

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
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label htmlFor="confirmPassword" style={styles.label}>
              Confirm password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              style={styles.input}
            />
          </div>

          {error && (
            <p role="alert" style={styles.error}>
              {error}
            </p>
          )}

          {success && (
            <p role="status" style={styles.success}>
              {success}
            </p>
          )}

          <button type="submit" disabled={isSubmitting} style={styles.button}>
            {isSubmitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p style={styles.footerText}>
          Already have an account? <Link to="/login" style={styles.link}>Log in.</Link>
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
  success: {
    fontSize: '13px',
    color: 'var(--color-success)',
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
    fontWeight: 600,
    textDecoration: 'none',
  },
}