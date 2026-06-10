import type { FC } from 'react'
import { TECH_MARQUEE, TECHNOLOGIES } from '../data/content'
import Reveal from './Reveal'
import SectionTitle from './SectionTitle'

const Technologies: FC = () => {
  return (
    <section id="tecnologias" className="retro-grid relative bg-[#050505] py-24 overflow-hidden">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle
          eyebrow="NUESTRO ARSENAL"
          title="TECNOLOGÍAS"
          subtitle="El stack que dominamos para construir soluciones robustas y escalables."
        />
      </div>

      {/* Marquee infinito de tecnologías */}
      <div className="relative mb-16 border-y-2 border-primary/40 bg-black py-4">
        <div className="marquee-track flex w-max gap-8">
          {[...TECH_MARQUEE, ...TECH_MARQUEE].map((tech, i) => (
            <span key={`${tech}-${i}`} className="flex items-center gap-3 whitespace-nowrap">
              <span className="h-2 w-2 bg-accent" aria-hidden="true" />
              <span className="font-brand text-[10px] text-cream">{tech.toUpperCase()}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {TECHNOLOGIES.map((group, i) => (
            <Reveal key={group.category} delay={(i % 3) * 100}>
              <div className="group h-full border-2 border-zgray/30 bg-black p-6 transition-colors hover:border-accent">
                <h3 className="font-brand text-[11px] text-accent group-hover:text-primary transition-colors">
                  ▸ {group.category.toUpperCase()}
                </h3>
                <ul className="mt-4 flex flex-wrap gap-2">
                  {group.items.map((item) => (
                    <li
                      key={item}
                      className="cursor-default border border-zgray/40 bg-[#0a0a0a] px-3 py-1.5 text-sm text-zgray transition-all duration-200 hover:-translate-y-0.5 hover:border-primary hover:text-primary"
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Technologies
