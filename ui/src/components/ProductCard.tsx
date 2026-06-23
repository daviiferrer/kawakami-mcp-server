import { Check, Plus } from "lucide-react"
import { Badge } from "@openai/apps-sdk-ui/components/Badge"
import { Button } from "@openai/apps-sdk-ui/components/Button"

import { IMG_BASE, activePrice, fmt, type Product } from "../data"

interface Props {
  product: Product
  isInCart: boolean
  isLoading: boolean
  onAdd: (product: Product) => void
}

const TAG_COLOR = {
  exclusive: "secondary",
  club: "warning",
  weekly: "success",
} as const

export function ProductCard({ product, isInCart, isLoading, onAdd }: Props) {
  const price = activePrice(product)
  const outOfStock = product.stock === 0
  const actionLabel = outOfStock
    ? `${product.name} está indisponível`
    : isInCart
      ? `Adicionar mais uma unidade de ${product.name}`
      : `Adicionar ${product.name} ao carrinho`

  return (
    <article className="min-w-[210px] max-w-[210px] flex-shrink-0 snap-start rounded-2xl border border-default bg-surface text-default overflow-hidden flex flex-col">
      <div className="relative flex h-[140px] items-center justify-center border-b border-default bg-surface-secondary shrink-0">
        <img
          src={`${IMG_BASE}/${product.image}`}
          alt={product.name}
          loading="lazy"
          className="max-h-[100px] max-w-[90%] object-contain"
        />
      </div>
      <div className="flex flex-1 flex-col gap-1 px-3 pt-2.5 pb-3">
        {product.tagLabel && (
          <Badge color={TAG_COLOR[product.tag!]} variant="solid" size="sm" className="self-start">
            {product.tagLabel}
          </Badge>
        )}
        <p className="line-clamp-2 text-sm font-medium leading-snug">{product.name}</p>
        {product.stock > 0 && product.stock <= 10 && (
          <p className="text-2xs text-warning">Apenas {product.stock} unidade{product.stock !== 1 ? "s" : ""}</p>
        )}
        <div className="flex items-end justify-between gap-2 mt-auto">
          <div className="whitespace-nowrap leading-none">
            {product.originalPrice && product.offerPrice && (
              <p className="text-2xs text-tertiary line-through">{fmt(product.originalPrice)}</p>
            )}
            <p className={`heading-sm ${product.offerPrice ? "text-success" : ""}`}>{fmt(price)}</p>
            <p className="text-2xs text-tertiary">/{product.unit}</p>
          </div>
          <Button
            color={isInCart ? "success" : "secondary"}
            variant={isInCart ? "solid" : "outline"}
            size="xs"
            uniform
            pill
            disabled={isLoading || outOfStock}
            onClick={() => onAdd(product)}
            aria-label={actionLabel}
            title={actionLabel}
            className={`shrink-0 ${isLoading ? "animate-pulse" : ""}`}
          >
            {outOfStock ? "—" : isInCart ? <Check className="size-4 animate-pulse" /> : <Plus className="size-4" />}
          </Button>
        </div>
      </div>
    </article>
  )
}
