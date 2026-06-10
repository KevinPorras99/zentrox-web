import type { FC } from 'react'
import { PIXEL_ICONS, PROJECTS } from '../data/content'
import PixelArt from './PixelArt'
import Reveal from './Reveal'
import SectionTitle from './SectionTitle'

const Portfolio: FC = () => {
  return (
    <section id="portafolio" className="relative bg-black py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle
          eyebrow="NUESTRO TRABAJO"
          title="PORTAFOLIO"
          subtitle="Proyectos que combinan ingeniería sólida con experiencias memorables."
        />

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          {PROJECTS.map((project, i) => (
            <Reveal key={project.id} delay={(i % 2) * 120}>
              <article className="group pixel-corners overflow-hidden border-2 border-zgray/30 bg-[#0a0a0a] transition-all duration-300 hover:border-primary hover:shadow-[0_0_24px_rgba(255,216,5,0.2)]">
                {/* Miniatura pixel art */}
                <div className="scanlines relative flex h-44 items-center justify-center bg-gradient-to-br from-[#1a1400] via-black to-[#170e00]">
                  <div className="transition-transform duration-300 group-hover:scale-125">
                    <PixelArt matrix={PIXEL_ICONS[project.icon]} size={9} label={project.title} />
                  </div>
                  <span className="absolute top-3 left-3 z-10 bg-accent px-2 py-1 font-brand text-[8px] text-black">
                    {project.tag.toUpperCase()}
                  </span>
                </div>

                <div className="p-6">
                  <h3 className="font-brand text-xs leading-relaxed text-cream group-hover:text-primary transition-colors">
                    {project.title.toUpperCase()}
                  </h3>
                  <p className="mt-3 text-sm leading-relaxed text-zgray">{project.description}</p>
                  <ul className="mt-4 flex flex-wrap gap-2">
                    {project.stack.map((tech) => (
                      <li
                        key={tech}
                        className="border border-primary/50 px-2 py-1 text-[11px] text-primary"
                      >
                        {tech}
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Portfolio
