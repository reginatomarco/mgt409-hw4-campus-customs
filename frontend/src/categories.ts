// Groups the catalogue's messy garment_type values into a few shopper-friendly categories.

export interface Category {
  slug: string
  label: string
  match: (garmentType: string, name: string) => boolean
}

export const CATEGORIES: Category[] = [
  { slug: 'hoodies', label: 'Hoodies', match: (t, n) => /hood/.test(t) || /hood/.test(n) },
  { slug: 'crewnecks', label: 'Crewnecks', match: (t) => /crew|mockneck/.test(t) && !/t-shirt/.test(t) },
  { slug: 'tees', label: 'Tees', match: (t) => /t-shirt/.test(t) },
  { slug: 'quarter-zips', label: 'Quarter-Zips', match: (t) => /quarter-zip/.test(t) },
  { slug: 'outerwear', label: 'Fleece & Jackets', match: (t) => /fleece|jacket/.test(t) },
  { slug: 'performance', label: 'Performance', match: (t) => /long-sleeve/.test(t) },
]

export function categoryOf(garmentType: string, name: string): Category | undefined {
  const t = garmentType.toLowerCase()
  const n = name.toLowerCase()
  return CATEGORIES.find((c) => c.match(t, n))
}
