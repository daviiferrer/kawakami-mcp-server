import { Check } from "lucide-react"
import { useEffect, useState } from "react"

interface Props {
  text: string
  onDone: () => void
}

export function Toast({ text, onDone }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const showTimer = setTimeout(() => setVisible(true), 50)
    const hideTimer = setTimeout(() => setVisible(false), 1800)
    const doneTimer = setTimeout(onDone, 2100)
    return () => {
      clearTimeout(showTimer)
      clearTimeout(hideTimer)
      clearTimeout(doneTimer)
    }
  }, [onDone])

  return (
    <div
      className={`pointer-events-none fixed bottom-24 left-1/2 z-[60] flex -translate-x-1/2 items-center gap-1.5 whitespace-nowrap rounded-full bg-emerald-600 px-4 py-2 text-xs font-semibold text-white transition-opacity ${
        visible ? "opacity-100" : "opacity-0"
      }`}
    >
      <Check className="size-3.5" />
      {text}
    </div>
  )
}
