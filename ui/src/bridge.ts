import type { Product } from "./data"
import type { CartItem } from "./components/CartDrawer"

export interface UiSection {
  key: string
  title: string
  products: Product[]
}

export interface ToolResultLike {
  structuredContent?: unknown
  content?: unknown
  isError?: boolean
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null
}

export function readSections(result: ToolResultLike): UiSection[] | null {
  if (!isRecord(result.structuredContent)) return null
  const sections = result.structuredContent.sections
  return Array.isArray(sections) ? (sections as UiSection[]) : null
}

export function readCart(result: ToolResultLike): CartItem[] | null {
  if (!isRecord(result.structuredContent)) return null
  const cart = result.structuredContent.cart
  return Array.isArray(cart) ? (cart as CartItem[]) : null
}

export function readSessionId(result: ToolResultLike): string | null {
  if (!isRecord(result.structuredContent)) return null
  const sessionId = result.structuredContent.sessionId
  return typeof sessionId === "string" ? sessionId : null
}

export function readError(result: ToolResultLike): string | null {
  if (!result.isError || !Array.isArray(result.content)) return null
  const first = result.content[0]
  if (!isRecord(first)) return "Falha ao executar a operacao."
  return typeof first.text === "string" ? first.text : "Falha ao executar a operacao."
}
