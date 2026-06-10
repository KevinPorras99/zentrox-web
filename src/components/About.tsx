import type { FC } from 'react'
import { COMPANY, PIXEL_ICONS } from '../data/content'
import PixelArt from './PixelArt'
import Reveal from './Reveal'
import SectionTitle from './SectionTitle'

const PILLARS = [
  {
    icon: 'robot',
    title: 'MISIÓN',
    text: 'Transformar ideas en soluciones digitales innovadoras que impulsen el crecimiento de cada negocio, combinando software a medida e inteligencia artificial con un servicio cercano y de calidad.',
  },
  {
    icon: 'cloud',
    title: 'VISIÓN',
    text: 'Ser la empresa de desarrollo de software e IA de referencia en Costa Rica y la región, reconocida por su excelencia técnica, creatividad y compromiso con el éxito de sus clientes.',
  },
  {
    icon: 'shield',
    title: 'VALORES',
    text: 'Innovación constante, transparencia con el cliente, calidad en cada línea de código y pasión por la tecnología — con identidad propia y carácter retro-gamer.',
  },
] as const

const About: FC = () => {
  return (
    <section id="nosotros" className="retro-grid relative bg-[#050505] py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle
          eyebrow="QUIÉNES SOMOS"
          title="SOBRE NOSOTROS"
          subtitle={`${COMPANY.name} es una empresa de desarrollo de software e inteligencia artificial con base en ${COMPANY.location}.`}
        />

        <Reveal>
          <div className="pixel-corners mx-auto mb-14 max-w-3xl border-2 border-accent/50 bg-black p-8 text-center">
            <p className="text-base leading-relaxed text-zgray sm:text-lg">
              Nacimos con una idea clara:{' '}
              <span className="text-cream font-semibold">la tecnología no tiene por qué ser aburrida</span>. Unimos la
              ingeniería de software moderna —web, móvil, cloud e inteligencia artificial— con una identidad
              retro-arcade que nos distingue. Cada proyecto es una nueva partida, y{' '}
              <span className="text-primary font-semibold">jugamos para ganar contigo</span>.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {PILLARS.map((pillar, i) => (
            <Reveal key={pillar.title} delay={i * 120}>
              <div className="group h-full border-2 border-zgray/30 bg-black p-6 text-center transition-colors hover:border-primary">
                <div className="mb-4 flex justify-center transition-transform duration-300 group-hover:scale-110">
                  <PixelArt matrix={PIXEL_ICONS[pillar.icon]} size={5} label={pillar.title} />
                </div>
                <h3 className="font-brand text-sm text-primary">{pillar.title}</h3>
                <p className="mt-4 text-sm leading-relaxed text-zgray">{pillar.text}</p>
              </div>
            </Reveal>
          ))}
        </div>

        {/* Contador estilo arcade */}
        <Reveal delay={200}>
          <div className="mt-14 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { value: '10+', label: 'Servicios' },
              { value: '15+', label: 'Tecnologías' },
              { value: '100%', label: 'Compromiso' },
              { value: '24/7', label: 'Soporte' },
            ].map((stat) => (
              <div key={stat.label} className="border-2 border-accent/40 bg-black p-5 text-center">
                <p className="font-brand text-lg text-primary sm:text-xl">{stat.value}</p>
                <p className="mt-2 text-xs uppercase tracking-widest text-zgray">{stat.label}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}

export default About
