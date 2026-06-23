import type { CartItem } from "./CartDrawer"
import { ProductCard } from "./ProductCard"
import type { Product } from "../data"

interface Props {
  products: Product[]
  cartItems: CartItem[]
  loadingIds: Set<number>
  onAdd: (product: Product) => void
}

export function ProductCarousel({ products, cartItems, loadingIds, onAdd }: Props) {
  const inCartIds = new Set(cartItems.map((item) => item.id))

  return (
    <div className="flex snap-x snap-mandatory gap-2.5 overflow-x-auto px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden md:flex-wrap md:overflow-x-visible md:snap-none md:gap-3">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          isInCart={inCartIds.has(product.id)}
          isLoading={loadingIds.has(product.id)}
          onAdd={onAdd}
        />
      ))}
    </div>
  )
}
