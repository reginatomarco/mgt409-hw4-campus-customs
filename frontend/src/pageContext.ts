// Builds the "what's on screen" summary the chat sends with every message (backend PageContext),
// so the assistant can tell what "this", "it" or "these" refers to.

import type { ChatResults } from './chatResults'

export type PageType =
  | 'home'
  | 'products'
  | 'assistant_results'
  | 'product'
  | 'about'
  | 'login'
  | 'create_account'
  | 'other'

export interface PageContext {
  page: PageType
  viewing_product_id: string | null
  selected_size: string | null
  search_text: string | null
  category: string | null
  results_label: string | null
  results_product_ids: string[]
}

export function buildPageContext(pathname: string, search: string, chatResults: ChatResults | null): PageContext {
  const params = new URLSearchParams(search)
  const productId = pathname.match(/^\/products\/([^/]+)$/)?.[1] ?? null
  const showingResults = pathname === '/products' && params.get('view') === 'chat' && chatResults !== null

  let page: PageType = 'other'
  if (pathname === '/') page = 'home'
  else if (productId) page = 'product'
  else if (showingResults) page = 'assistant_results'
  else if (pathname === '/products') page = 'products'
  else if (pathname === '/about') page = 'about'
  else if (pathname === '/login') page = 'login'
  else if (pathname === '/create-account') page = 'create_account'

  return {
    page,
    viewing_product_id: productId ? decodeURIComponent(productId) : null,
    selected_size: productId ? params.get('size') : null,
    search_text: page === 'products' ? params.get('q') : null,
    category: page === 'products' ? params.get('category') : null,
    results_label: showingResults ? chatResults.label : null,
    results_product_ids: showingResults ? chatResults.products.slice(0, 6).map((p) => p.product_id) : [],
  }
}
