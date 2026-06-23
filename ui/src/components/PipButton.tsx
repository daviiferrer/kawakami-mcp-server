import { ShoppingCart } from "lucide-react"

interface Props {
  count: number
  onClick: () => void
}

export function PipButton({ count, onClick }: Props) {
  if (count === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-30">
      <button
        type="button"
        aria-label="Abrir carrinho"
        onClick={onClick}
        className="grid size-12 place-items-center rounded-full bg-emerald-600 text-white shadow-lg transition hover:bg-emerald-700"
      >
        <ShoppingCart className="size-5" />
      </button>
      <span className="pointer-events-none absolute -right-1 -top-1 min-w-5 rounded-full bg-red-600 px-1.5 py-0.5 text-center text-xs font-bold text-white">
        {count}
      </span>
    </div>
  )
}
