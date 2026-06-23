export interface Product {
  id: number
  name: string
  price: number
  offerPrice: number | null
  originalPrice: number | null
  unit: string
  image: string
  stock: number
  tag: "exclusive" | "club" | "weekly" | null
  tagLabel: string | null
}

export const IMG_BASE =
  "https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250"

export function fmt(value: number): string {
  return `R$ ${value.toFixed(2).replace(".", ",")}`
}

export function activePrice(product: Product): number {
  return product.offerPrice ?? product.price
}
