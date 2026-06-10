import type { FC } from 'react'
import { PIXEL_ICONS, SERVICES } from '../data/content'
import PixelArt from './PixelArt'
import Reveal from './Reveal'
import SectionTitle from './SectionTitle'

const Services: FC = () => {
  return (
    <section id="servicios" className="relative bg-black py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle
          eyebrow="LO QUE HACEMOS"
          title="SERVICIOS"
          subtitle="Diez líneas de servicio para llevar tu negocio al siguiente nivel."
        />

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((service, i) => (
            <Reveal key={service.id} delay={(i % 3) * 100}>
              <article className="group pixel-corners h-full border-2 border-zgray/30 bg-[#0a0a0a] p-6 transition-all duration-300 hover:border-primary hover:bg-[#111] hover:shadow-[0_0_24px_rgba(255,216,5,0.25)]">
                <div className="mb-4 flex items-center justify-between">
                  <div className="transition-transform duration-300 group-hover:scale-110">
                    <PixelArt matrix={PIXEL_ICONS[service.icon]} size={4} label={service.title} />
                  </div>
                  <span className="font-brand text-[10px] text-zgray/60 group-hover:text-accent transition-colors">
                    {String(service.id).padStart(2, '0')}
                  </span>
                </div>
                <h3 className="font-brand text-[11px] leading-relaxed text-cream group-hover:text-primary transition-colors">
                  {service.title.toUpperCase()}
                </h3>
                <p className="mt-3 text-sm text-zgray">{service.description}</p>
                <div className="mt-4 h-1 w-0 bg-accent transition-all duration-300 group-hover:w-full" />
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Services
