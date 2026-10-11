import type { ReactNode } from 'react'

export default function AuthLayout({ quote, perks, children }: { quote: string; perks: string[]; children: ReactNode }) {
  return (
    <section className="auth-page">
      <aside className="auth-aside">
        <span className="brand-mark">CC</span>
        <p className="auth-quote">{quote}</p>
        <ul>
          {perks.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>
      </aside>
      <div className="auth-main">{children}</div>
    </section>
  )
}
