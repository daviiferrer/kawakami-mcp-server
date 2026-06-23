import type { Product } from "../data"
import { ProductCard } from "./ProductCard"

interface Props { products: Product[]; cartItems: { id: number }[]; onAdd: (id: number) => void }

export function ProductCarousel({ products, cartItems, onAdd }: Props) {
  const inCartIds = new Set(cartItems.map(c => c.id))
  return (
    <div className="flex gap-2.5 overflow-x-auto pb-6 px-4 snap-x snap-mandatory [scrollbar-width:none] [&::-webkit-scrollbar]:hidden md:flex-wrap md:overflow-x-visible md:snap-none md:justify-center md:gap-3">
      {products.map(p => <ProductCard key={p.id} product={p} isInCart={inCartIds.has(p.id)} onAdd={onAdd} />)}
    </div>
  )
}
