import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getJson, imageUrl, type Product } from '../api'
import { CATEGORIES, categoryOf } from '../categories'
import ProductTile from '../components/ProductTile'

// Hand-picked for the hero collage and the featured row.
const HERO_IDS = ['district-vit-hoodie-vintage-bulldog', 'super-heavyweight-crewneck-arched-yale-crest', 'brooks-brothers-bomber-jacket-yale']
const FEATURED_IDS = [
  'basic-hoodie-big-yale',
  'district-vit-crewneck-vintage-standing-bulldog',
  '2025-yale-vs-harvard-t-shirt',
  'brooks-brothers-bomber-jacket-yale',
]

const SLOGANS = [
  'Casual comfort. Unbreakable Bulldog pride.',
  'Boola Boola.',
  'Harvard sees this and reconsiders.',
  'Built for New Haven winters.',
  'Hood up. Distractions down.',
  'Rep your college.',
]

const PILLARS = [
  { icon: '🏋️', title: 'Heavyweight only', text: 'Crewnecks that never skip leg day. Put one on and your posture fixes itself.' },
  { icon: '🏛️', title: 'Every college', text: 'Berkeley to Trumbull. Rep the crest. Your college deserves loyalty.' },
  { icon: '🏈', title: 'Game day armor', text: 'Football, hockey, lacrosse, sailing. Wear it to The Game. Harvard will notice.' },
  { icon: '👨‍👩‍👧', title: 'The whole family', text: 'Yale Mom, Dad, Grandpa, Aunt. Being a Yale parent is a rank, not a title.' },
]

export default function Home() {
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    getJson<Product[]>('/api/products').then(setProducts).catch(() => setProducts([]))
  }, [])

  const byId = new Map(products.map((p) => [p.product_id, p]))
  const hero = HERO_IDS.map((id) => byId.get(id)).filter((p): p is Product => !!p)
  const featured = FEATURED_IDS.map((id) => byId.get(id)).filter((p): p is Product => !!p)

  // One cover image and a count for each category tile.
  const categoryTiles = CATEGORIES.map((c) => {
    const items = products.filter((p) => categoryOf(p.garment_type, p.name)?.slug === c.slug)
    return { ...c, count: items.length, cover: items[0] }
  }).filter((c) => c.count > 0)

  return (
    <>
      <section className="hero full-bleed">
        <div className="hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">Officially licensed · Est. on Broadway</p>
            <h1>
              Some people wear clothes.
              <span>Bulldogs wear a legacy.</span>
            </h1>
            <p className="hero-lead">
              Heavyweight hoodies, crest crewnecks and game day tees for students, parents and alumni. No mid
              fabrics. No hesitation. Just Bulldog Blue.
            </p>
            <div className="hero-actions">
              <Link to="/products" className="btn btn-light">Shop the drip</Link>
              <Link to="/about" className="btn btn-outline">Read the legend</Link>
            </div>
            <dl className="hero-stats">
              <div><dt>{products.length || 102}</dt><dd>styles</dd></div>
              <div><dt>14</dt><dd>colleges</dd></div>
              <div><dt>XS–XXL</dt><dd>sizes</dd></div>
            </dl>
          </div>
          <div className="hero-collage" aria-hidden="true">
            {hero.map((p, i) => (
              <div key={p.product_id} className={`collage-card c${i}`}>
                <img src={imageUrl(p.image_file_path)} alt="" />
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="ticker full-bleed" aria-hidden="true">
        <div className="ticker-track">
          {[...SLOGANS, ...SLOGANS].map((s, i) => (
            <span key={i}>{s} <b>✦</b></span>
          ))}
        </div>
      </div>

      <section className="section">
        <div className="section-head">
          <h2>Shop by category</h2>
          <Link to="/products" className="link-arrow">See everything →</Link>
        </div>
        <div className="category-grid">
          {categoryTiles.map((c) => (
            <Link key={c.slug} to={`/products?category=${c.slug}`} className="category-tile">
              {c.cover && <img src={imageUrl(c.cover.image_file_path)} alt="" loading="lazy" />}
              <div>
                <h3>{c.label}</h3>
                <span>{c.count} styles</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {featured.length > 0 && (
        <section className="section">
          <div className="section-head">
            <h2>Certified bangers</h2>
            <Link to="/products" className="link-arrow">Shop all →</Link>
          </div>
          <div className="tile-grid">
            {featured.map((p) => (
              <ProductTile key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}

      <section className="section">
        <div className="pillar-grid">
          {PILLARS.map((p) => (
            <article key={p.title} className="pillar">
              <span className="pillar-icon">{p.icon}</span>
              <h3>{p.title}</h3>
              <p>{p.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="promo">
        <div>
          <p className="eyebrow">Family Weekend</p>
          <h2>Your parents are coming. Prepare accordingly.</h2>
          <p>
            Mom wants a Yale Mom hoodie. Dad wants to act like he's not proud. Get them sorted before they land in
            New Haven.
          </p>
        </div>
        <Link to="/products?q=yale%20mom" className="btn btn-light">Shop family gear</Link>
      </section>
    </>
  )
}
