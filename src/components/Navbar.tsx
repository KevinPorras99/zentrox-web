import { useEffect, useState } from 'react'
import type { FC } from 'react'
import { NAV_LINKS, PIXEL_ICONS } from '../data/content'
import PixelArt from './PixelArt'

/** Navbar sticky: transparente arriba, fondo negro + borde dorado al hacer scroll. */
const Navbar: FC = () => {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-black/95 border-b-2 border-primary shadow-[0_4px_0_0_rgba(244,159,32,0.4)]'
          : 'bg-transparent border-b-2 border-transparent'
      }`}
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <a href="#inicio" className="flex items-center gap-3 group" aria-label="Zentrox — Inicio">
          <PixelArt matrix={PIXEL_ICONS.invader} size={3} className="pixel-float" label="Logo Zentrox" />
          <span className="font-brand text-primary text-sm sm:text-base group-hover:text-accent transition-colors">
            ZENTROX
          </span>
        </a>

        {/* Navegación escritorio */}
        <ul className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm text-zgray hover:text-primary transition-colors font-medium tracking-wide"
              >
                {link.label}
              </a>
            </li>
          ))}
          <li>
            <a
              href="#contacto"
              className="pixel-corners bg-primary px-4 py-2 text-xs font-brand text-black hover:bg-accent transition-colors"
            >
              CONTÁCTANOS
            </a>
          </li>
        </ul>

        {/* Botón menú móvil */}
        <button
          type="button"
          className="md:hidden text-primary font-brand text-lg p-2"
          onClick={() => setMenuOpen((open) => !open)}
          aria-expanded={menuOpen}
          aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </nav>

      {/* Menú móvil */}
      {menuOpen && (
        <ul className="md:hidden bg-black border-t border-accent/40 px-6 pb-4">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                onClick={() => setMenuOpen(false)}
                className="block py-3 text-sm text-zgray hover:text-primary transition-colors border-b border-white/5"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      )}
    </header>
  )
}

export default Navbar
