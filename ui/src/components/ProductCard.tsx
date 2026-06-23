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
  club: "bg-amber-500 text-zinc-950",
  weekly: "bg-emerald-600",
} as const

export function ProductCard({ product, isInCart, isLoading, onAdd }: Props) {
  const price = activePrice(product)
  const tagClass = product.tag ? TAG_CLASSES[product.tag] : ""

  return (
    <article className="min-w-[210px] max-w-[210px] flex-shrink-0 snap-start overflow-hidden rounded-xl border border-zinc-200 bg-white text-zinc-950 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100">
      <div className="relative flex h-[140px] items-center justify-center border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
        <img
          src={`${IMG_BASE}/${product.image}`}
          alt={product.name}
          loading="lazy"
          className="max-h-[100px] max-w-[90%] object-contain"
        />
        {product.tagLabel && (
          <span
            className={`absolute left-2 top-2 rounded-full px-2 py-1 text-[10px] font-bold text-white ${tagClass}`}
          >
            {product.tagLabel}
          </span>
        )}
      </div>
      <div className="flex min-h-[150px] flex-col px-3 pb-3 pt-2.5">
        <p className="mb-1 line-clamp-2 min-h-[38px] text-sm font-medium">{product.name}</p>
        <p className="mb-2.5 text-xs text-zinc-500">{product.stock} em estoque</p>
        <div className="mt-auto flex items-end justify-between gap-2">
          <div className="whitespace-nowrap">
            {product.originalPrice && product.offerPrice && (
              <p className="text-xs leading-none text-zinc-500 line-through">
                {fmt(product.originalPrice)}
              </p>
            )}
            <p className="text-lg font-bold leading-tight">{fmt(price)}</p>
            <p className="text-xs text-zinc-500">/{product.unit}</p>
          </div>
          <button
            type="button"
            disabled={isLoading}
            onClick={() => onAdd(product)}
            className="inline-flex items-center gap-1 rounded-lg border border-emerald-600 px-2.5 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50 disabled:cursor-wait disabled:opacity-50 dark:text-emerald-400 dark:hover:bg-emerald-950"
          >
            {isInCart ? <Check className="size-3.5" /> : <Plus className="size-3.5" />}
            Adicionar
          </button>
        </div>
      </div>
    </article>
  )
}
