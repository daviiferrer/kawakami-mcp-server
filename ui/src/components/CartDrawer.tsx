import { Minus, Plus, ShoppingCart, Trash2, X } from "lucide-react"
import { Button } from "@openai/apps-sdk-ui/components/Button"
import { AnimateLayoutGroup } from "@openai/apps-sdk-ui/components/Transition"

import { IMG_BASE, fmt } from "../data"

export interface CartItem {
  id: number
  name: string
  unit: string
  unitPrice: number
  quantity: number
  subtotal: number
  image: string
  isOffer: boolean
  originalPrice: number | null
}

interface Props {
  items: CartItem[]
  open: boolean
  loadingIds: Set<number>
  onClose: () => void
  onQuantityChange: (item: CartItem, delta: number) => void
  onRemove: (item: CartItem) => void
}

export function CartDrawer({
  items,
  open,
  loadingIds,
  onClose,
  onQuantityChange,
  onRemove,
}: Props) {
  const total = items.reduce((sum, item) => sum + item.subtotal, 0)
  const unitCount = items.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <>
      <div
        aria-hidden="true"
        className={`fixed inset-0 z-40 transition ${
          open ? "pointer-events-auto bg-black/50" : "pointer-events-none bg-transparent"
        }`}
        onClick={onClose}
      />
      <aside
        className={`fixed inset-x-0 bottom-0 z-50 flex max-h-[90dvh] flex-col bg-surface text-default shadow-2xl transition-transform duration-300 sm:left-1/2 sm:max-w-[480px] sm:-translate-x-1/2 sm:rounded-t-2xl ${
          open ? "translate-y-0" : "translate-y-full"
        }`}
      >
        <header className="flex items-center justify-between border-b border-default px-4 py-3">
          <h2 className="heading-md">Carrinho</h2>
          <Button color="primary" variant="ghost" uniform size="sm" onClick={onClose}>
            <X className="size-5" />
          </Button>
        </header>
        <div className="flex-1 overflow-y-auto px-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-16 text-tertiary">
              <ShoppingCart className="size-10 opacity-40" />
              <p className="text-sm">Carrinho vazio</p>
            </div>
          ) : (
            <AnimateLayoutGroup
              enter={{ y: -8, opacity: 0, duration: 250 }}
              exit={{ opacity: 0, duration: 200 }}
              layoutEnter={{ duration: 300 }}
            >
              {items.map((item) => {
                const isLoading = loadingIds.has(item.id)
                return (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 border-b border-subtle py-3"
                  >
                    <img
                      src={`${IMG_BASE}/${item.image}`}
                      alt={item.name}
                      className="size-14 rounded-lg bg-surface-secondary object-contain"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{item.name}</p>
                      <p className="text-xs text-tertiary">
                        {fmt(item.unitPrice)}/{item.unit}
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <Button color="primary" variant="ghost" uniform size="xs" disabled={isLoading} onClick={() => onQuantityChange(item, -1)}>
                          <Minus className="size-3" />
                        </Button>
                        <span className="min-w-5 text-center text-sm font-bold">{item.quantity}</span>
                        <Button color="primary" variant="ghost" uniform size="xs" disabled={isLoading} onClick={() => onQuantityChange(item, 1)}>
                          <Plus className="size-3" />
                        </Button>
                      </div>
                    </div>
                    <p className="heading-xs text-success">{fmt(item.subtotal)}</p>
                    <Button color="primary" variant="ghost" uniform size="xs" disabled={isLoading} onClick={() => onRemove(item)}>
                      <Trash2 className="size-4 text-tertiary" />
                    </Button>
                  </div>
                )
              })}
            </AnimateLayoutGroup>
          )}
        </div>
        <footer className="border-t-2 border-success px-4 py-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-secondary">Total</p>
              <p className="text-xs text-tertiary">
                {unitCount} unidade{unitCount !== 1 ? "s" : ""}
              </p>
            </div>
            <p className="heading-lg text-success">{fmt(total)}</p>
          </div>
          <p className="mt-3 text-xs text-tertiary">
            Carrinho salvo nesta sessão. O Kawakami não oferece checkout por esta integração.
          </p>
        </footer>
      </aside>
    </>
  )
}
