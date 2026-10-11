import { Link } from 'react-router-dom'
import { imageUrl, type Product } from '../api'
import { categoryOf } from '../categories'

interface Props {
  product: Product
  showBlurb?: boolean
  fromChat?: boolean // opened from the assistant's results, so the product page can link back
}

export default function ProductTile({ product, showBlurb = true, fromChat = false }: Props) {
  const category = categoryOf(product.garment_type, product.name)
  return (
    <Link to={`/products/${product.product_id}`} state={fromChat ? { fromChat: true } : undefined} className="tile">
      <div className="tile-media">
        <img src={imageUrl(product.image_file_path)} alt={product.name} loading="lazy" />
        {category && <span className="tile-tag">{category.label}</span>}
      </div>
      <div className="tile-body">
        <h3>{product.name}</h3>
        {showBlurb && <p className="tile-blurb">{product.blurb}</p>}
        <div className="tile-footer">
          <span className="tile-price">${product.price.toFixed(0)}</span>
          <span className="tile-cta">View →</span>
        </div>
      </div>
    </Link>
  )
}
