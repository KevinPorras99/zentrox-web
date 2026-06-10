import type { FC } from 'react'
import Reveal from './Reveal'

interface SectionTitleProps {
  eyebrow: string
  title: string
  subtitle?: string
}

/** Encabezado de sección con estilo arcade consistente. */
const SectionTitle: FC<SectionTitleProps> = ({ eyebrow, title, subtitle }) => (
  <Reveal className="mb-14 text-center">
    <p className="font-brand text-[10px] tracking-widest text-accent">★ {eyebrow} ★</p>
    <h2 className="mt-4 font-brand text-xl text-primary sm:text-2xl md:text-3xl drop-shadow-[3px_3px_0_rgba(244,159,32,0.4)]">
      {title}
    </h2>
    {subtitle && <p className="mx-auto mt-5 max-w-2xl text-sm text-zgray sm:text-base">{subtitle}</p>}
    <div className="mx-auto mt-6 flex w-fit gap-1">
      {[...Array(5)].map((_, i) => (
        <span key={i} className={`h-2 w-2 ${i % 2 === 0 ? 'bg-primary' : 'bg-accent'}`} />
      ))}
    </div>
  </Reveal>
)

export default SectionTitle
