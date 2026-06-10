import type { FC } from 'react'
import { COMPANY, NAV_LINKS, PIXEL_ICONS } from '../data/content'
import PixelArt from './PixelArt'

const SOCIAL_LINKS = [
  { label: 'GitHub', href: 'https://github.com' },
  { label: 'LinkedIn', href: 'https://linkedin.com' },
  { label: 'Instagram', href: 'https://instagram.com' },
] as const

const Footer: FC = () => {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t-2 border-primary bg-[#050505]">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-3">
          {/* Marca */}
          <div>
            <div className="flex items-center gap-3">
              <PixelArt matrix={PIXEL_ICONS.invader} size={3} label="Logo Zentrox" />
              <span className="font-brand text-sm text-primary">ZENTROX</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-zgray">{COMPANY.slogan}</p>
            <p className="mt-2 text-xs text-zgray/70">{COMPANY.location}</p>
          </div>

          {/* Navegación */}
          <nav aria-label="Enlaces del pie de página">
            <h3 className="font-brand text-[10px] text-cream">NAVEGACIÓN</h3>
            <ul className="mt-4 grid grid-cols-2 gap-2">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a href={link.href} className="text-sm text-zgray hover:text-primary transition-colors">
                    ▸ {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          {/* Redes */}
          <div>
            <h3 className="font-brand text-[10px] text-cream">SÍGUENOS</h3>
            <ul className="mt-4 flex gap-3">
              {SOCIAL_LINKS.map((social) => (
                <li key={social.label}>
                  <a
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="pixel-corners inline-block border-2 border-zgray/40 px-3 py-2 text-xs text-zgray transition-colors hover:border-primary hover:text-primary"
                  >
                    {social.label}
                  </a>
                </li>
              ))}
            </ul>
            <a
              href={`mailto:${COMPANY.email}`}
              className="mt-4 block text-sm text-zgray hover:text-primary transition-colors break-all"
            >
              {COMPANY.email}
            </a>
          </div>
        </div>

        <div className="mt-12 border-t border-zgray/20 pt-6 text-center">
          <p className="font-brand text-[9px] leading-relaxed text-zgray">
            © {year} ZENTROX — TODOS LOS DERECHOS RESERVADOS
          </p>
          <p className="mt-2 text-xs text-zgray/60">
            Hecho con <span className="text-primary">♥</span> y muchos píxeles en Costa Rica
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
