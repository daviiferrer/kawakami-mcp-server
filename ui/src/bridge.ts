import { type Product } from "./data"

export interface UiSection { key: string; title: string; products: Product[] }

type Listener = () => void
let _sections: UiSection[] = []
const listeners = new Set<Listener>()

export function onSectionsChange(fn: Listener): () => void {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export function getSections(): UiSection[] {
  return _sections
}

function notify() {
  for (const fn of listeners) fn()
}

function handleMessage(e: MessageEvent) {
  const msg = e.data
  if (!msg || typeof msg !== "object") return

  switch (msg.type) {
    case "ui/render":
      if (msg.section && Array.isArray(msg.products)) {
        _sections = [{ key: msg.section, title: msg.title || msg.section, products: msg.products as Product[] }]
        notify()
      }
      break
    case "ui/render_multi":
      if (Array.isArray(msg.sections)) {
        _sections = msg.sections as UiSection[]
        notify()
      }
      break
    case "ui/clear":
      _sections = []
      notify()
      break
  }
}

window.addEventListener("message", handleMessage)
