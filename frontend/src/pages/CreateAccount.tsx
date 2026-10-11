import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import { useAuth, type RegisterForm } from '../authContext'

export default function CreateAccount() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<RegisterForm>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const update = (field: keyof RegisterForm) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [field]: e.target.value })

  const mismatch = form.confirm_password !== '' && form.password !== form.confirm_password

  // Same rules the backend enforces (backend/auth.py), shown live as a checklist.
  const rules = [
    { label: 'At least 8 characters', ok: form.password.length >= 8 },
    { label: 'A letter', ok: /\p{L}/u.test(form.password) },
    { label: 'A number', ok: /\d/.test(form.password) },
    { label: 'A special character (! @ # $ ...)', ok: /[^\p{L}\p{N}\s]/u.test(form.password) },
  ]
  const strong = rules.every((r) => r.ok)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (mismatch || !strong) return
    setError(null)
    setSubmitting(true)
    try {
      await register(form)
      navigate('/products')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout
      quote="Every legend starts with a sign-up form."
      perks={['An assistant that remembers you', 'Saved chat history', 'Zero spam. We respect the grind.']}
    >
      <h1>Create Account</h1>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-row">
          <label>
            First name
            <input autoComplete="given-name" value={form.first_name} onChange={update('first_name')} required />
          </label>
          <label>
            Last name
            <input autoComplete="family-name" value={form.last_name} onChange={update('last_name')} required />
          </label>
        </div>
        <label>
          Email
          <input type="email" autoComplete="email" value={form.email} onChange={update('email')} required />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={update('password')}
            minLength={8}
            maxLength={128}
            required
          />
          <ul className="password-rules" aria-live="polite">
            {rules.map((r) => (
              <li key={r.label} className={r.ok ? 'ok' : undefined}>
                {r.ok ? '✓' : '○'} {r.label}
              </li>
            ))}
          </ul>
        </label>
        <label>
          Confirm password
          <input
            type="password"
            autoComplete="new-password"
            value={form.confirm_password}
            onChange={update('confirm_password')}
            required
          />
        </label>
        {mismatch && <p className="error">Passwords don't match.</p>}
        <button type="submit" className="btn btn-dark btn-block" disabled={submitting || mismatch || !strong}>
          {submitting ? 'Creating...' : 'Create account'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
      <p className="muted">
        Already one of us? <Link to="/login">Log in</Link>
      </p>
    </AuthLayout>
  )
}
