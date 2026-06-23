import { useApp, useHostStyles } from "@modelcontextprotocol/ext-apps/react"
import { useCallback, useEffect, useRef, useState } from "react"

import {
  readCart,
  readError,
  readSections,
  readSessionId,
  type ToolResultLike,
  type UiSection,
} from "./bridge"
import { CartDrawer, type CartItem } from "./components/CartDrawer"
import { PipButton } from "./components/PipButton"
import { ProductCarousel } from "./components/ProductCarousel"
import { Toast } from "./components/Toast"
import type { Product } from "./data"

export function App() {
  const [sections, setSections] = useState<UiSection[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [toast, setToast] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [loadingIds, setLoadingIds] = useState<Set<number>>(new Set())
  const isCreatingSession = useRef(false)

  const applyToolResult = useCallback((result: ToolResultLike) => {
    const error = readError(result)
    if (error) {
      setErrorMessage(error)
      return
    }
    const nextSections = readSections(result)
    const nextCart = readCart(result)
    const nextSessionId = readSessionId(result)
    if (nextSections) setSections(nextSections)
    if (nextCart) setCart(nextCart)
    if (nextSessionId) setSessionId(nextSessionId)
  }, [])

  const { app, isConnected, error } = useApp({
    appInfo: { name: "Kawakami Catalog", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (createdApp) => {
      createdApp.ontoolresult = applyToolResult
    },
  })
  useHostStyles(app, app?.getHostContext())

  useEffect(() => {
    if (!app || !isConnected || sessionId || isCreatingSession.current) return
    isCreatingSession.current = true
    void app
      .callServerTool({ name: "criar_sessao", arguments: {} })
      .then(applyToolResult)
      .catch((sessionError: unknown) => {
        setErrorMessage(
          sessionError instanceof Error ? sessionError.message : "Falha ao criar sessão.",
        )
      })
      .finally(() => {
        isCreatingSession.current = false
      })
  }, [app, applyToolResult, isConnected, sessionId])

  const runProductMutation = useCallback(
    async (productId: number, name: string, quantity: number): Promise<void> => {
      if (!app || !sessionId) return
      setLoadingIds((current) => new Set(current).add(productId))
      setErrorMessage(null)
      try {
        const result =
          quantity <= 0
            ? await app.callServerTool({
                name: "remover_do_carrinho",
                arguments: { session_id: sessionId, termo: name },
              })
            : await app.callServerTool({
                name: "adicionar_ao_carrinho",
                arguments: {
                  session_id: sessionId,
                  termo: name,
                  quantidade: quantity,
                },
              })
        applyToolResult(result)
      } catch (mutationError) {
        setErrorMessage(
          mutationError instanceof Error ? mutationError.message : "Falha ao atualizar carrinho.",
        )
      } finally {
        setLoadingIds((current) => {
          const next = new Set(current)
          next.delete(productId)
          return next
        })
      }
    },
    [app, applyToolResult, sessionId],
  )

  const addToCart = useCallback(
    (product: Product) => {
      const existing = cart.find((item) => item.id === product.id)
      setToast(product.name)
      void runProductMutation(product.id, product.name, (existing?.quantity ?? 0) + 1)
    },
    [cart, runProductMutation],
  )

  const changeQuantity = useCallback(
    (item: CartItem, delta: number) => {
      void runProductMutation(item.id, item.name, item.quantity + delta)
    },
    [runProductMutation],
  )

  const removeItem = useCallback(
    (item: CartItem) => {
      void runProductMutation(item.id, item.name, 0)
    },
    [runProductMutation],
  )

  const unitCount = cart.reduce((sum, item) => sum + item.quantity, 0)
  const connectionError = error?.message ?? errorMessage

  if (!isConnected && !connectionError) {
    return <p className="p-6 text-center text-sm text-tertiary">Conectando ao Kawakami...</p>
  }

  return (
    <main className="min-h-dvh bg-main text-default">
      {connectionError && (
        <p className="mx-4 mt-4 rounded-lg bg-red-100 px-3 py-2 text-sm text-red-800 dark:bg-red-950 dark:text-red-200">
          {connectionError}
        </p>
      )}
      {sections.length === 0 ? (
        <p className="py-20 text-center text-sm text-tertiary">Nenhum produto para exibir.</p>
      ) : (
        sections.map((section) => (
          <section key={section.key}>
            <h2 className="px-4 pb-2.5 pt-4 text-xs font-semibold uppercase tracking-wider text-tertiary">
              {section.title}
            </h2>
            <ProductCarousel
              products={section.products}
              cartItems={cart}
              loadingIds={loadingIds}
              onAdd={addToCart}
            />
          </section>
        ))
      )}
      <div className="h-4" />
      <PipButton count={unitCount} onClick={() => setDrawerOpen(true)} />
      <CartDrawer
        items={cart}
        open={drawerOpen}
        loadingIds={loadingIds}
        onClose={() => setDrawerOpen(false)}
        onQuantityChange={changeQuantity}
        onRemove={removeItem}
      />
      {toast && <Toast text={toast} onDone={() => setToast(null)} />}
    </main>
  )
}
