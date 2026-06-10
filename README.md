# Zentrox — Sitio Web Oficial

> **SOLUCIONES TECNOLÓGICAS INTELIGENTES**
> Transformamos ideas en soluciones digitales innovadoras.

Sitio web corporativo de **Zentrox** (Alajuela, Costa Rica) con identidad retro-arcade / pixel art.

## Stack

- **React 19 + TypeScript** (Vite)
- **Tailwind CSS v4** con la paleta oficial como tokens de tema
- Animaciones CSS + canvas (partículas pixel, glitch, scanlines, marquee)

## Paleta oficial

| Color | Hex | Uso |
| --- | --- | --- |
| Primary Gold | `#ffd805` | Textos destacados, CTAs |
| Orange Accent | `#f49f20` | Acentos, hover |
| Light Cream | `#ffe37c` | Fondos secundarios |
| Gray | `#afafaf` | Textos secundarios |
| Black | `#000000` | Fondo principal |

## Desarrollo

```bash
npm install
npm run dev      # servidor de desarrollo (http://localhost:5173)
npm run build    # build de producción en dist/
```

## Estructura

```
src/
├── components/   # Navbar, Hero, Services, About, Portfolio, Technologies, Contact, Footer
│   ├── PixelArt.tsx   # renderiza matrices de caracteres como pixel art SVG
│   └── Reveal.tsx     # animaciones de entrada al hacer scroll
├── data/content.ts    # servicios, tecnologías, proyectos e íconos pixel
└── hooks/useReveal.ts # IntersectionObserver para reveals
```

© Zentrox — Hecho con ♥ y muchos píxeles en Costa Rica.
