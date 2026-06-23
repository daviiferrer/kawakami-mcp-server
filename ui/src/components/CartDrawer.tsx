import { X, Minus, Plus, CreditCard, ShoppingCart, Trash2 } from "lucide-react"
import { Button } from "@openai/apps-sdk-ui/components/Button"
import { AnimateLayoutGroup } from "@openai/apps-sdk-ui/components/Transition"
import { fmt, IMG_BASE } from "../data"

export interface CartItem { id: number; name: string; unit: string; unitPrice: number; quantity: number; subtotal: number; image: string; isOffer: boolean; originalPrice: number | null }

interface Props { items: CartItem[]; open: boolean; onClose: () => void; onQuantityChange: (id: number, delta: number) => void; onRemove: (id: number) => void; onCheckout: () => void }

export function CartDrawer({ items, open, onClose, onQuantityChange, onRemove, onCheckout }: Props) {
  const total = items.reduce((s, i) => s + i.subtotal, 0)
  const unitCount = items.reduce((s, i) => s + i.quantity, 0)
  return (
    <>
      <div className={`fixed inset-0 z-40 transition-all duration-300 ${open ? "bg-black/50 pointer-events-auto" : "bg-transparent pointer-events-none"}`} onClick={onClose} />
      <div className={`fixed inset-x-0 bottom-0 z-50 bg-surface flex flex-col max-h-[90dvh] transition-transform duration-[350ms] ease-[cubic-bezier(0.19,1,0.22,1)] sm:max-w-[480px] sm:left-1/2 sm:-translate-x-1/2 sm:rounded-t-2xl ${open ? "translate-y-0" : "translate-y-full"}`}>
        <div className="flex justify-center pt-3 pb-1 flex-shrink-0"><div className="w-9 h-1 bg-default/20 rounded-full" /></div>
        <div className="flex items-center justify-between px-4 py-3 border-b border-default flex-shrink-0">
          <h2 className="heading-md">Carrinho</h2>
          <Button variant="ghost" uniform size="sm" onClick={onClose}><X className="size-5" /></Button>
        </div>
        <div className="flex-1 overflow-y-auto px-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-16 text-tertiary"><ShoppingCart className="size-10 opacity-40" /><p className="text-sm">Carrinho vazio</p></div>
          ) : (
            <AnimateLayoutGroup enter={{ y: -8, opacity: 0, duration: 250 }} exit={{ opacity: 0, duration: 200 }} layoutEnter={{ duration: 300 }}>
              {items.map(item => (
                <div key={item.id} className="flex items-center gap-3 py-3 border-b border-subtle">
                  <img src={`${IMG_BASE}/${item.image}`} alt={item.name} className="w-14 h-14 object-contain bg-surface-secondary rounded-lg border border-default flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.name}</p>
                    <p className="text-xs text-tertiary mt-0.5">{fmt(item.unitPrice)}/{item.unit}</p>
                    <div className="flex items-center gap-1.5 mt-1.5">
                      <Button variant="ghost" uniform size="xs" onClick={() => onQuantityChange(item.id, -1)}><Minus className="size-3" /></Button>
                      <span className="text-sm font-bold min-w-[20px] text-center">{item.quantity}</span>
                      <Button variant="ghost" uniform size="xs" onClick={() => onQuantityChange(item.id, 1)}><Plus className="size-3" /></Button>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className={`heading-xs ${item.isOffer ? "text-success" : ""}`}>{fmt(item.subtotal)}</p>
                    {item.isOffer && item.originalPrice && <p className="text-2xs text-tertiary line-through">{fmt(item.originalPrice * item.quantity)}</p>}
                  </div>
                  <Button variant="ghost" uniform size="xs" onClick={() => onRemove(item.id)}><Trash2 className="size-4 text-tertiary" /></Button>
                </div>
              ))}
            </AnimateLayoutGroup>
          )}
        </div>
        <div className="px-4 py-4 border-t-2 border-success flex-shrink-0">
          <div className="flex justify-between items-end mb-3">
            <div><p className="text-xs text-secondary uppercase tracking-wider font-semibold">Total</p><p className="text-xs text-tertiary mt-0.5">{unitCount} unidade{unitCount !== 1 ? "s" : ""}</p></div>
            <p className="heading-lg text-success">{fmt(total)}</p>
          </div>
          <Button color="primary" variant="solid" size="lg" block disabled={items.length === 0} onClick={onCheckout}><CreditCard className="size-5" /> Finalizar Compra</Button>
        </div>
      </div>
    </>
  )
}
