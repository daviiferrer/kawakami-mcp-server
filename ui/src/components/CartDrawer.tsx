import { Minus, Plus, ShoppingCart, Trash2, X } from "lucide-react"

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
      <button
        type="button"
        aria-label="Fechar carrinho"
        className={`fixed inset-0 z-40 transition ${
          open ? "pointer-events-auto bg-black/50" : "pointer-events-none bg-transparent"
        }`}
        onClick={onClose}
      />
      <aside
        className={`fixed inset-x-0 bottom-0 z-50 flex max-h-[90dvh] flex-col bg-white text-zinc-950 shadow-2xl transition-transform duration-300 dark:bg-zinc-900 dark:text-zinc-100 sm:left-1/2 sm:max-w-[480px] sm:-translate-x-1/2 sm:rounded-t-2xl ${
          open ? "translate-y-0" : "translate-y-full"
        }`}
      >
        <header className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
          <h2 className="text-lg font-bold">Carrinho</h2>
          <button type="button" aria-label="Fechar" onClick={onClose} className="p-2">
            <X className="size-5" />
          </button>
        </header>
        <div className="flex-1 overflow-y-auto px-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-16 text-zinc-500">
              <ShoppingCart className="size-10 opacity-40" />
              <p className="text-sm">Carrinho vazio</p>
            </div>
          ) : (
            items.map((item) => {
              const isLoading = loadingIds.has(item.id)
              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 border-b border-zinc-200 py-3 dark:border-zinc-800"
                >
                  <img
                    src={`${IMG_BASE}/${item.image}`}
                    alt={item.name}
                    className="size-14 rounded-lg bg-zinc-50 object-contain dark:bg-zinc-950"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-zinc-500">
                      {fmt(item.unitPrice)}/{item.unit}
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <button
                        type="button"
                        disabled={isLoading}
                        onClick={() => onQuantityChange(item, -1)}
                        className="rounded border border-zinc-300 p-1 disabled:opacity-50 dark:border-zinc-700"
                      >
                        <Minus className="size-3" />
                      </button>
                      <span className="min-w-5 text-center text-sm font-bold">{item.quantity}</span>
                      <button
                        type="button"
                        disabled={isLoading}
                        onClick={() => onQuantityChange(item, 1)}
                        className="rounded border border-zinc-300 p-1 disabled:opacity-50 dark:border-zinc-700"
                      >
                        <Plus className="size-3" />
                      </button>
                    </div>
                  </div>
                  <p className="font-bold text-emerald-600">{fmt(item.subtotal)}</p>
                  <button
                    type="button"
                    aria-label={`Remover ${item.name}`}
                    disabled={isLoading}
                    onClick={() => onRemove(item)}
                    className="p-1 text-zinc-500 disabled:opacity-50"
                  >
                    <Trash2 className="size-4" />
                  </button>
                </div>
              )
            })
          )}
        </div>
        <footer className="border-t-2 border-emerald-600 px-4 py-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Total</p>
              <p className="text-xs text-zinc-500">
                {unitCount} unidade{unitCount !== 1 ? "s" : ""}
              </p>
            </div>
            <p className="text-2xl font-bold text-emerald-600">{fmt(total)}</p>
          </div>
          <p className="mt-3 text-xs text-zinc-500">
            Carrinho salvo nesta sessão. O Kawakami não oferece checkout por esta integração.
          </p>
        </footer>
      </aside>
    </>
  )
}
