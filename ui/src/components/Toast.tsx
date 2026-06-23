import { useEffect, useState } from "react"
import { Check } from "lucide-react"

interface Props { text: string; onDone: () => void }

export function Toast({ text, onDone }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t0 = setTimeout(() => setVisible(true), 50)
    const t1 = setTimeout(() => setVisible(false), 1800)
    const t2 = setTimeout(() => onDone(), 2100)
    return () => { clearTimeout(t0); clearTimeout(t1); clearTimeout(t2) }
  }, [onDone])

  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-[60] bg-success text-white px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition-opacity duration-200 pointer-events-none ${visible ? "opacity-100" : "opacity-0"}`}>
      <Check className="size-3.5" /> {text}
    </div>
  )
}
