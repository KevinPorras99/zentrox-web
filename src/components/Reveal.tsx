import type { FC, ReactNode } from 'react'
import { useReveal } from '../hooks/useReveal'

interface RevealProps {
  children: ReactNode
  /** Retraso en ms para escalonar animaciones */
  delay?: number
  className?: string
}

/** Envoltorio que aplica fade-in + slide-up cuando el elemento entra al viewport. */
const Reveal: FC<RevealProps> = ({ children, delay = 0, className = '' }) => {
  const { ref, visible } = useReveal<HTMLDivElement>()

  return (
    <div
      ref={ref}
      className={`reveal ${visible ? 'visible' : ''} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

export default Reveal
