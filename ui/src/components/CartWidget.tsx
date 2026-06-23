import { CartCard } from "./CartCard"
import type { CartItem } from "./CartDrawer"
import { fmt } from "../data"

interface Props {
  items: CartItem[]
  loadingIds: Set<number>
  onQuantityChange: (item: CartItem, delta: number) => void
  onRemove: (item: CartItem) => void
}

const COLUMN_SIZE = 3

function chunked<T>(arr: T[], size: number): T[][] {
  const out: T[][] = []
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size))
  }
  return out
}

export function CartWidget({ items, loadingIds, onQuantityChange, onRemove }: Props) {
  if (items.length === 0) return null

  const columns = chunked(items, COLUMN_SIZE)
  const total = items.reduce((sum, item) => sum + item.subtotal, 0)
  const unitCount = items.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <div>
      <div className="flex snap-x snap-mandatory gap-2.5 overflow-x-auto px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {columns.map((col, ci) => (
          <div key={ci} className="flex shrink-0 snap-start flex-col gap-2.5">
            {col.map((item) => (
              <CartCard
                key={item.id}
                item={item}
                isLoading={loadingIds.has(item.id)}
                onQuantityChange={onQuantityChange}
                onRemove={onRemove}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mx-4 rounded-2xl border-2 border-success bg-surface px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-secondary">Total</p>
            <p className="text-2xs text-tertiary">
              {unitCount} unidade{unitCount !== 1 ? "s" : ""}
            </p>
          </div>
          <p className="heading-lg text-success">{fmt(total)}</p>
        </div>
      </div>
    </div>
  )
}
