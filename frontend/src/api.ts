// Shapes and helpers for talking to the FastAPI backend (proxied by Vite).

export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_file_path: string
  price: number
  blurb: string
}

export interface StockLevel {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  inventory: StockLevel[]
}

export interface ProductCard {
  product_id: string
  name: string
  garment_type: string
  price: number
  colors: string[]
  image_file_path: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products: ProductCard[]
  pageResultsTotal?: number // set when this reply sent search results to the Products page
}

export interface PageResults {
  label: string // summary of the search, e.g. "hoodie · under $70"
  total: number
  products: Product[]
}

export interface ChatResponse {
  reply: string
  products: ProductCard[]
  page_results: PageResults | null
  saved: boolean
}

export async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(res.status === 404 ? 'Not found' : `Request failed (${res.status})`)
  return res.json()
}

// image_file_path looks like "products/x.jpg"; the backend serves data/ at /images.
export const imageUrl = (path: string) => `/images/${path}`

export async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new Error(errorMessage(data?.detail) ?? `Request failed (${res.status})`)
  }
  return res.json()
}

// FastAPI sends a string for our own errors and a list for validation errors.
function errorMessage(detail: unknown): string | undefined {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return String(detail[0].msg ?? '').replace(/^Value error, /, '') || undefined
  }
  return undefined
}
