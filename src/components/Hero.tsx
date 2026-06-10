import { useEffect, useRef } from 'react'
import type { FC } from 'react'
import { COMPANY, PIXEL_ICONS } from '../data/content'
import PixelArt from './PixelArt'
import PixelScene from './PixelScene'

interface Particle {
  x: number
  y: number
  size: number
  speed: number
  color: string
  drift: number
}

const PARTICLE_COLORS = ['#ffd805', '#f49f20', '#ffe37c', '#afafaf'] as const

/** Lluvia de píxeles dorados estilo arcade sobre canvas. */
const PixelParticles: FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let raf = 0
    let particles: Particle[] = []

    const resize = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      const count = Math.floor(canvas.width / 18)
      particles = Array.from({ length: count }, () => spawn(true))
    }

    const spawn = (anywhere = false): Particle => ({
      x: Math.random() * canvas.width,
      y: anywhere ? Math.random() * canvas.height : -8,
      size: Math.random() < 0.7 ? 3 : 5,
      speed: 0.3 + Math.random() * 0.9,
      color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
      drift: (Math.random() - 0.5) * 0.3,
    })

    const tick = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]
        p.y += p.speed
        p.x += p.drift
        if (p.y > canvas.height + 8) particles[i] = spawn()
        ctx.fillStyle = p.color
        ctx.globalAlpha = 0.7
        // Píxeles alineados a una cuadrícula para mantener el look 8-bit
        ctx.fillRect(Math.round(p.x / p.size) * p.size, Math.round(p.y / p.size) * p.size, p.size, p.size)
      }
      ctx.globalAlpha = 1
      raf = requestAnimationFrame(tick)
    }

    resize()
    tick()
    window.addEventListener('resize', resize)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-hidden="true" />
}

const Hero: FC = () => {
  return (
    <section
      id="inicio"
      className="scanlines relative flex min-h-screen items-center justify-center overflow-hidden bg-black"
    >
      {/* Ciudad pixel-art al atardecer (estilo lofi, paleta Zentrox) */}
      <PixelScene seed={7} variant="sunset" className="absolute inset-0 h-full w-full object-cover" />
      {/* Velo oscuro para legibilidad del texto sobre la escena */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/40 to-black/10" />
      <PixelParticles />

      <div className="relative z-10 mx-auto max-w-4xl px-4 py-28 text-center sm:px-6">
        {/* Mascota pixel art */}
        <div className="mb-8 flex justify-center gap-6">
          <PixelArt matrix={PIXEL_ICONS.invader} size={6} className="pixel-float hidden sm:block" />
          <PixelArt
            matrix={PIXEL_ICONS.invader}
            size={8}
            className="pixel-float"
            label="Mascota pixel de Zentrox"
          />
          <PixelArt matrix={PIXEL_ICONS.invader} size={6} className="pixel-float hidden sm:block" />
        </div>

        <p className="font-brand text-accent text-[10px] sm:text-xs mb-6 tracking-widest">
          ★ ZENTROX — ALAJUELA, COSTA RICA ★
        </p>

        <h1 className="font-brand text-primary text-xl leading-relaxed sm:text-3xl md:text-4xl md:leading-relaxed drop-shadow-[4px_4px_0_rgba(244,159,32,0.5)]">
          {COMPANY.headline}
        </h1>

        <p className="blink-cursor mx-auto mt-8 max-w-xl text-base text-zgray sm:text-lg">
          {COMPANY.slogan}
        </p>

        <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a
            href="#contacto"
            className="pixel-corners glitch-hover w-full bg-primary px-8 py-4 font-brand text-xs text-black transition-colors hover:bg-accent sm:w-auto"
          >
            ▶ CONTÁCTANOS
          </a>
          <a
            href="#servicios"
            className="pixel-corners w-full border-2 border-primary px-8 py-4 font-brand text-xs text-primary transition-colors hover:bg-primary hover:text-black sm:w-auto"
          >
            VER SERVICIOS
          </a>
        </div>

        {/* Indicador de scroll */}
        <a
          href="#servicios"
          className="mt-16 inline-block animate-bounce font-brand text-2xl text-accent"
          aria-label="Bajar a servicios"
        >
          ▼
        </a>
      </div>
    </section>
  )
}

export default Hero
