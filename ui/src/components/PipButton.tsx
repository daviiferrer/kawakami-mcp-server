import { ShoppingCart } from "lucide-react"
import { Badge } from "@openai/apps-sdk-ui/components/Badge"
import { Button } from "@openai/apps-sdk-ui/components/Button"

interface Props {
  count: number
  onClick: () => void
}

export function PipButton({ count, onClick }: Props) {
  if (count === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-30">
      <Button color="primary" variant="solid" size="xl" uniform pill onClick={onClick} aria-label="Abrir carrinho">
        <ShoppingCart className="size-5" />
      </Button>
      <div className="absolute -top-1 -right-1 pointer-events-none">
        <Badge color="danger" variant="solid">{count}</Badge>
      </div>
    </div>
  )
}
