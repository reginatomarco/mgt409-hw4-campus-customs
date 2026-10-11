import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getJson, type Product } from '../api'
import { CATEGORIES, categoryOf } from '../categories'
import { clearChatResults, useChatResults } from '../chatResults'
import ProductTile from '../components/ProductTile'

type Sort = 'featured' | 'price-asc' | 'price-desc' | 'name'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  // Filters live in the URL so links like /products?category=hoodies work and survive a refresh.
  const [params, setParams] = useSearchParams()
  const category = params.get('category') ?? 'all'
  const query = params.get('q') ?? ''
  const sort = (params.get('sort') as Sort) ?? 'featured'
  const chatResults = useChatResults()
  const showChatResults = params.get('view') === 'chat' && chatResults !== null

  useEffect(() => {
    getJson<Product[]>('/api/products')
      .then(setProducts)
      .catch(() => setError("Couldn't reach the backend. Make sure the FastAPI server is running."))
      .finally(() => setLoading(false))
  }, [])

  function setParam(key: string, value: string, empty: string) {
    const next = new URLSearchParams(params)
    if (value === empty) next.delete(key)
    else next.set(key, value)
    setParams(next, { replace: true })
  }

  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  const visible = products
    .filter((p) => category === 'all' || categoryOf(p.garment_type, p.name)?.slug === category)
    .filter((p) => {
      const text = `${p.name} ${p.garment_type} ${p.description} ${p.colors.join(' ')} ${p.search_tags.join(' ')}`.toLowerCase()
      return words.every((w) => text.includes(w))
    })
    .sort((a, b) => {
      if (sort === 'price-asc') return a.price - b.price
      if (sort === 'price-desc') return b.price - a.price
      if (sort === 'name') return a.name.localeCompare(b.name)
      return 0
    })

  const counts = new Map<string, number>()
  for (const p of products) {
    const slug = categoryOf(p.garment_type, p.name)?.slug
    if (slug) counts.set(slug, (counts.get(slug) ?? 0) + 1)
  }

  if (showChatResults) {
    const shown = chatResults.products.length
    return (
      <section>
        <header className="page-head">
          <p className="eyebrow dark">Found by the assistant</p>
          <h1>Assistant results</h1>
        </header>

        <div className="chat-results-banner" aria-live="polite">
          <span className="chat-avatar" aria-hidden="true">🐶</span>
          <div>
            <p className="chat-results-question">“{chatResults.question}”</p>
            <p className="chat-results-meta">
              {chatResults.total} {chatResults.total === 1 ? 'match' : 'matches'} for <strong>{chatResults.label}</strong>
              {shown < chatResults.total && ` · showing the first ${shown}`}
            </p>
          </div>
          <div className="chat-results-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setParam('view', 'all', 'all')}>
              Browse all products
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => {
                clearChatResults()
                setParam('view', 'all', 'all')
              }}
            >
              Clear results
            </button>
          </div>
        </div>

        <div className="tile-grid">
          {chatResults.products.map((p) => (
            <ProductTile key={p.product_id} product={p} fromChat />
          ))}
        </div>
      </section>
    )
  }

  return (
    <section>
      <header className="page-head">
        <p className="eyebrow dark">The armory</p>
        <h1>Products</h1>
        <p className="lead">Every piece built for one thing: being the most Yale person in the room.</p>
      </header>

      {chatResults && (
        <button type="button" className="chat-results-return" onClick={() => setParam('view', 'chat', '')}>
          🐶 Back to the assistant's results for “{chatResults.question}” ({chatResults.total})
        </button>
      )}

      <div className="toolbar">
        <div className="search-box">
          <span aria-hidden="true">⌕</span>
          <input
            type="search"
            placeholder="Search bulldog, Saybrook, hockey..."
            value={query}
            onChange={(e) => setParam('q', e.target.value, '')}
            aria-label="Search products"
          />
        </div>
        <select value={sort} onChange={(e) => setParam('sort', e.target.value, 'featured')} aria-label="Sort products">
          <option value="featured">Sort: Featured</option>
          <option value="price-asc">Price: low to high</option>
          <option value="price-desc">Price: high to low</option>
          <option value="name">Name: A to Z</option>
        </select>
      </div>

      <div className="chip-row" role="tablist" aria-label="Categories">
        <button
          type="button"
          className={`filter-chip ${category === 'all' ? 'active' : ''}`}
          onClick={() => setParam('category', 'all', 'all')}
        >
          All <span>{products.length}</span>
        </button>
        {CATEGORIES.filter((c) => counts.get(c.slug)).map((c) => (
          <button
            key={c.slug}
            type="button"
            className={`filter-chip ${category === c.slug ? 'active' : ''}`}
            onClick={() => setParam('category', c.slug, 'all')}
          >
            {c.label} <span>{counts.get(c.slug)}</span>
          </button>
        ))}
      </div>

      {loading && (
        <div className="tile-grid">
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className="tile skeleton" />
          ))}
        </div>
      )}
      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <>
          <p className="result-count">
            {visible.length} {visible.length === 1 ? 'style' : 'styles'}
          </p>
          {visible.length === 0 ? (
            <div className="empty">
              <h3>Nothing here. Even legends strike out sometimes.</h3>
              <p>Try a different word, or ask the assistant in the bottom-right corner.</p>
            </div>
          ) : (
            <div className="tile-grid">
              {visible.map((p) => (
                <ProductTile key={p.product_id} product={p} />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
