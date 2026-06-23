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
  const actionLabel = isInCart
    ? `Adicionar mais uma unidade de ${product.name}`
    : `Adicionar ${product.name} ao carrinho`

  return (
    <article className="min-w-[210px] max-w-[210px] flex-shrink-0 snap-start overflow-hidden rounded-2xl border border-default bg-surface text-default">
      <div className="relative flex h-[140px] items-center justify-center border-b border-default bg-surface-secondary">
        <img
          src={`${IMG_BASE}/${product.image}`}
          alt={product.name}
          loading="lazy"
          className="max-h-[100px] max-w-[90%] object-contain"
        />
      </div>
      <div className="flex min-h-[150px] flex-col px-3 pb-3 pt-2.5">
        {product.tagLabel && (
          <Badge color={TAG_COLOR[product.tag!]} variant="solid" size="sm" className="-mt-5 mb-1.5 self-start">
            {product.tagLabel}
          </Badge>
        )}
        <p className="mb-1 line-clamp-2 min-h-[38px] text-sm font-medium">{product.name}</p>
        <p className="mb-2.5 text-2xs text-tertiary">{product.stock} em estoque</p>
        <div className="mt-auto flex items-end justify-between gap-2">
          <div className="whitespace-nowrap">
            {product.originalPrice && product.offerPrice && (
              <p className="text-2xs text-tertiary line-through">
                {fmt(product.originalPrice)}
              </p>
            )}
            <p className="heading-sm">{fmt(price)}</p>
            <p className="text-2xs text-tertiary">/{product.unit}</p>
          </div>
          <Button
            color={isInCart ? "success" : "secondary"}
            variant={isInCart ? "solid" : "outline"}
            size="xs"
            uniform
            pill
            disabled={isLoading}
            onClick={() => onAdd(product)}
            aria-label={actionLabel}
            title={actionLabel}
          >
            {isInCart ? <Check className="size-4" /> : <Plus className="size-4" />}
          </Button>
        </div>
      </div>
    </article>
  )
}
