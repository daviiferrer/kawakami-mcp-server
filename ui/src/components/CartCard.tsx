import { Minus, Plus, Trash2 } from "lucide-react"
import { Badge } from "@openai/apps-sdk-ui/components/Badge"
import { Button } from "@openai/apps-sdk-ui/components/Button"

import { IMG_BASE, fmt } from "../data"
import type { CartItem } from "./CartDrawer"

interface Props {
  item: CartItem
  isLoading: boolean
  onQuantityChange: (item: CartItem, delta: number) => void
  onRemove: (item: CartItem) => void
}

export function CartCard({ item, isLoading, onQuantityChange, onRemove }: Props) {
  return (
    <article className="min-w-[210px] max-w-[210px] flex-shrink-0 rounded-2xl border border-default bg-surface text-default overflow-hidden">
      <div className="flex gap-2.5 px-3 py-2.5">
        <img
          src={`${IMG_BASE}/${item.image}`}
          alt={item.name}
          loading="lazy"
          className="size-12 shrink-0 rounded-lg bg-surface-secondary object-contain"
        />
        <div className="min-w-0 flex-1">
          <p className="line-clamp-2 text-xs font-medium leading-snug">{item.name}</p>
          <p className="text-2xs text-tertiary">{fmt(item.unitPrice)}/{item.unit}</p>
          {item.isOffer && (
            <Badge color="success" variant="solid" size="sm" className="mt-0.5">
              Oferta
            </Badge>
          )}
          <div className="mt-2 flex items-center justify-between">
            <div className="flex items-center gap-1">
              <Button
                color="primary"
                variant="ghost"
                uniform
                size="xs"
                disabled={isLoading}
                onClick={() => onQuantityChange(item, -1)}
                aria-label={`Remover uma unidade de ${item.name}`}
              >
                <Minus className="size-3" />
              </Button>
              <span className="min-w-4 text-center text-xs font-bold">{item.quantity}</span>
              <Button
                color="primary"
                variant="ghost"
                uniform
                size="xs"
                disabled={isLoading}
                onClick={() => onQuantityChange(item, 1)}
                aria-label={`Adicionar uma unidade de ${item.name}`}
              >
                <Plus className="size-3" />
              </Button>
            </div>
            <div className="flex items-center gap-1">
              <p className="heading-xs text-success">{fmt(item.subtotal)}</p>
              <Button
                color="primary"
                variant="ghost"
                uniform
                size="xs"
                disabled={isLoading}
                onClick={() => onRemove(item)}
                aria-label={`Remover ${item.name}`}
              >
                <Trash2 className="size-3 text-tertiary" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
