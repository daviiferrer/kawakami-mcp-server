import { Badge } from "@openai/apps-sdk-ui/components/Badge"
import { Button } from "@openai/apps-sdk-ui/components/Button"
import { Plus, Check } from "lucide-react"
import type { Product } from "../data"
import { IMG_BASE, fmt, activePrice } from "../data"

interface Props { product: Product; isInCart: boolean; onAdd: (id: number) => void }

const TAG_COLOR = { exclusive: "secondary", club: "warning", weekly: "success" } as const

export function ProductCard({ product, isInCart, onAdd }: Props) {
  const price = activePrice(product)
  return (
    <div className="min-w-[210px] max-w-[210px] flex-shrink-0 snap-start bg-surface border border-default rounded-xl overflow-hidden flex flex-col">
      <div className="relative bg-surface-secondary flex justify-center items-center h-[140px] border-b border-default flex-shrink-0">
        <img src={`${IMG_BASE}/${product.image}`} alt={product.name} loading="lazy" className="max-h-[100px] max-w-[90%] object-contain" />
        {product.tagLabel && (
          <Badge color={TAG_COLOR[product.tag!]} variant="solid" size="sm" className="absolute top-2 left-2">
            {product.tagLabel}
          </Badge>
        )}
      </div>
      <div className="px-3 pt-2.5 pb-3 flex flex-col flex-1">
        <p className="text-sm font-medium line-clamp-2 mb-1" style={{ minHeight: "38px" }}>{product.name}</p>
        <p className="text-2xs text-tertiary mb-2.5">{product.stock} em estoque</p>
        <div className="mt-auto flex justify-between items-end gap-1">
          <div className="whitespace-nowrap">
            {product.originalPrice && product.offerPrice && <p className="text-2xs text-tertiary line-through leading-none mb-0.5">{fmt(product.originalPrice)}</p>}
            <p className="heading-sm leading-none">{fmt(price)}</p>
            <p className="text-2xs text-tertiary">/{product.unit}</p>
          </div>
          <Button color={isInCart ? "success" : "secondary"} variant={isInCart ? "solid" : "outline"} size="sm" onClick={() => onAdd(product.id)} className="flex-shrink-0 whitespace-nowrap">
            {isInCart ? <Check className="size-3.5" /> : <Plus className="size-3.5" />} Adicionar
          </Button>
        </div>
      </div>
    </div>
  )
}
