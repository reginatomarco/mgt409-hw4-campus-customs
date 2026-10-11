import { useEffect, useState } from 'react'
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom'
import { getJson, imageUrl, type Product, type ProductDetail } from '../api'
import { categoryOf } from '../categories'
import { openChat } from '../chatEvents'
import ProductTile from '../components/ProductTile'

export default function ProductPage() {
  const { productId } = useParams()
  const location = useLocation()
  const fromChat = (location.state as { fromChat?: boolean } | null)?.fromChat === true
  // Remember which product id the result belongs to, so a stale result shows as loading.
  const [result, setResult] = useState<{ id?: string; product?: ProductDetail; error?: string }>({})
  const [related, setRelated] = useState<Product[]>([])
  // The chosen size lives in the URL (?size=L) so the chat can see it as page context.
  const [params, setParams] = useSearchParams()
  const size = params.get('size')
  const setSize = (s: string) => setParams({ size: s }, { replace: true, state: location.state })

  useEffect(() => {
    getJson<ProductDetail>(`/api/products/${productId}`)
      .then((product) => setResult({ id: productId, product }))
      .catch((err: Error) =>
        setResult({
          id: productId,
          error: err.message === 'Not found' ? "This product doesn't exist. Even legends get lost." : "Couldn't reach the backend.",
        }),
      )
    getJson<Product[]>('/api/products').then(setRelated).catch(() => setRelated([]))
  }, [productId])

  const current = result.id === productId ? result : {}
  const { product, error } = current

  if (error) {
    return (
      <section className="empty">
        <h3>{error}</h3>
        <Link to="/products" className="btn btn-dark">Back to Products</Link>
      </section>
    )
  }
  if (!product) return <div className="detail-skeleton skeleton" />

  const category = categoryOf(product.garment_type, product.name)
  const similar = related
    .filter((p) => p.product_id !== product.product_id && categoryOf(p.garment_type, p.name)?.slug === category?.slug)
    .slice(0, 4)
  const selected = product.inventory.find((s) => s.size === size)
  const totalStock = product.inventory.reduce((sum, s) => sum + s.quantity, 0)

  return (
    <>
      <nav className="breadcrumb" aria-label="Breadcrumb">
        {fromChat && (
          <>
            <Link to="/products?view=chat" className="breadcrumb-back">← Assistant results</Link>
            <span>|</span>
          </>
        )}
        <Link to="/products">Products</Link>
        {category && (
          <>
            <span>/</span>
            <Link to={`/products?category=${category.slug}`}>{category.label}</Link>
          </>
        )}
        <span>/</span>
        <span>{product.name}</span>
      </nav>

      <section className="product-detail">
        <div className="detail-media">
          <img src={imageUrl(product.image_file_path)} alt={product.name} />
        </div>

        <div className="detail-info">
          <p className="eyebrow dark">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price">${product.price.toFixed(2)}</p>
          <p className="detail-blurb">“{product.blurb}”</p>
          <p className="detail-desc">{product.description}</p>

          <div className="detail-block">
            <h4>Colors</h4>
            <div className="swatches">
              {product.colors.map((c) => (
                <span key={c} className="swatch-label">{c}</span>
              ))}
            </div>
          </div>

          <div className="detail-block">
            <h4>
              Size {selected && <span className="muted">· {selected.size}</span>}
            </h4>
            <div className="size-grid">
              {product.inventory.map((s) => (
                <button
                  key={s.size}
                  type="button"
                  className={`size-btn ${size === s.size ? 'active' : ''}`}
                  disabled={s.quantity === 0}
                  onClick={() => setSize(s.size)}
                  title={s.quantity === 0 ? 'Sold out' : `${s.quantity} in stock`}
                >
                  {s.size}
                </button>
              ))}
            </div>
            <p className="stock-note">
              {selected
                ? selected.quantity < 5
                  ? `🔥 Only ${selected.quantity} left in ${selected.size}. Move fast.`
                  : `✓ ${selected.size} is in stock.`
                : totalStock === 0
                  ? 'Sold out everywhere. Legends get restocked though.'
                  : 'Pick a size to check stock.'}
            </p>
          </div>

          <div className="detail-actions">
            <a
              className="btn btn-dark"
              href="https://maps.google.com/?q=57+Broadway,+New+Haven,+CT+06511"
              target="_blank"
              rel="noreferrer"
            >
              Grab it at 57 Broadway
            </a>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() =>
                openChat(
                  size
                    ? `Is the ${product.name} a good pick in ${size}? How does it fit?`
                    : `Tell me more about the ${product.name}. What goes well with it?`,
                )
              }
            >
              💬 Ask the assistant
            </button>
          </div>
        </div>
      </section>

      {similar.length > 0 && (
        <section className="section">
          <div className="section-head">
            <h2>More {category?.label.toLowerCase()}</h2>
            <Link to={`/products?category=${category?.slug}`} className="link-arrow">See all →</Link>
          </div>
          <div className="tile-grid">
            {similar.map((p) => (
              <ProductTile key={p.product_id} product={p} showBlurb={false} />
            ))}
          </div>
        </section>
      )}
    </>
  )
}
