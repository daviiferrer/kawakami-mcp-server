import { Check, Plus } from "lucide-react"

import { IMG_BASE, activePrice, fmt, type Product } from "../data"

interface Props {
  product: Product
  isInCart: boolean
  isLoading: boolean
  onAdd: (product: Product) => void
}

const TAG_CLASSES = {
  exclusive: "bg-violet-600",
  club: "bg-amber-500 text-gray-1000",
  weekly: "bg-success",
} as const

export function ProductCard({ product, isInCart, isLoading, onAdd }: Props) {
  const price = activePrice(product)
  const tagClass = product.tag ? TAG_CLASSES[product.tag] : ""
  const actionLabel = isInCart
    ? `Adicionar mais uma unidade de ${product.name}`
    : `Adicionar ${product.name} ao carrinho`
  const actionClass = isInCart
    ? "border-success bg-success text-white"
    : "border-default text-secondary hover:border-success hover:text-success"

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
          <span
            className={`-mt-5 mb-1.5 self-start rounded-full px-2 py-0.5 text-2xs font-bold text-white ${tagClass}`}
          >
            {product.tagLabel}
          </span>
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
          <button
            type="button"
            disabled={isLoading}
            onClick={() => onAdd(product)}
            aria-label={actionLabel}
            title={actionLabel}
            className={`inline-flex size-8 shrink-0 items-center justify-center rounded-full border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-success/50 disabled:cursor-wait disabled:opacity-50 ${actionClass}`}
          >
            {isInCart ? <Check className="size-4" /> : <Plus className="size-4" />}
          </button>
        </div>
      </div>
    </article>
  )
}
