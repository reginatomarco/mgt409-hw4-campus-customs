import { Link } from 'react-router-dom'

const CODE = [
  { n: '01', title: 'Quality only', text: 'Heavy fabric, clean prints, made to survive four winters and a Harvard game.' },
  { n: '02', title: 'Every Bulldog welcome', text: 'Students, families, faculty, alumni and the guy who just really likes dogs.' },
  { n: '03', title: 'Officially licensed', text: 'Real crests, real colors, zero knockoffs. A Bulldog does not wear counterfeit.' },
  { n: '04', title: 'Pride never sells out', text: 'Sizes sometimes do. Our assistant checks stock for you in seconds.' },
]

export default function About() {
  return (
    <>
      <section className="about-hero full-bleed">
        <div className="about-hero-inner">
          <p className="eyebrow">About Us</p>
          <h1>We didn't choose the Bulldog life. It chose us.</h1>
          <p className="hero-lead">Then we put it on a crewneck.</p>
        </div>
      </section>

      <section className="section about-split">
        <div>
          <h2>Who we are</h2>
          <p>
            Campus Customs is the Yale merch spot at <strong>57 Broadway</strong>, right in the middle of New Haven.
            Everything we sell is officially licensed, so the crest on your chest is the real deal.
          </p>
          <p>
            Tees, hoodies, crewnecks, quarter-zips, fleeces and jackets. Gear for every residential college, the grad
            schools, the varsity teams and every class year. First-year, proud parent or alum back for reunion, we
            have your fit.
          </p>
        </div>
        <blockquote className="pull-quote">
          “Lesser hoodies fold under pressure. Ours lock in until the final submit.”
          <cite>The Campus Customs Code, probably</cite>
        </blockquote>
      </section>

      <section className="section">
        <h2>The code</h2>
        <div className="code-grid">
          {CODE.map((c) => (
            <article key={c.n} className="code-card">
              <span className="code-n">{c.n}</span>
              <h3>{c.title}</h3>
              <p>{c.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="promo">
        <div>
          <p className="eyebrow">Come through</p>
          <h2>Swing by Broadway or shop right here.</h2>
          <p>Make an account and our assistant will remember you, your style and your hoodie problem.</p>
        </div>
        <Link to="/products" className="btn btn-light">Shop now</Link>
      </section>
    </>
  )
}
