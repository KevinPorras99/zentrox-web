# CLAUDE.md — Zentrox Web

Contexto completo para AI assistants: empresa, marca, codebase, convenciones y flujos de trabajo.

---

## 1. Sobre la Empresa

| Campo | Detalle |
| :---- | :---- |
| **Nombre** | Zentrox |
| **Tipo** | Empresa de Desarrollo de Software e Inteligencia Artificial |
| **Ubicación** | Alajuela, Costa Rica |
| **Correo** | kevinporras9906@gmail.com |
| **Teléfono** | +506 8645-7832 |
| **Eslogan** | "Transformamos ideas en soluciones digitales innovadoras." |
| **Headline principal** | SOLUCIONES TECNOLÓGICAS INTELIGENTES |

---

## 2. Identidad de Marca

### Paleta de colores (OBLIGATORIA — no inventar colores nuevos)

```
--color-primary:  #ffd805   ← dorado, textos destacados, CTAs, bordes activos
--color-accent:   #f49f20   ← naranja, íconos, hover states
--color-cream:    #ffe37c   ← fondos secundarios, gradientes suaves
--color-gray:     #afafaf   ← textos secundarios, bordes, decoraciones
--color-bg:       #000000   ← fondo principal
--color-text:     #ffffff   ← texto base
```

Estas variables están definidas en `src/index.css`. Usarlas siempre vía variable CSS o Tailwind arbitrario (`text-[#ffd805]`).

### Tipografía

```
--font-brand: 'Press Start 2P', monospace   ← títulos, marca, secciones hero
--font-body:  'Space Grotesk', sans-serif   ← cuerpo, descripciones, formularios
```

Ambas fuentes se cargan desde Google Fonts en `index.html`.

### Estética

- Retro-arcade / 8-bit / pixel art — minimalista, profesional
- Alto contraste negro/dorado
- Pixel art generativo (SVG matrices + canvas procedural)
- CRT scanlines, glitch hover, floating animations

---

## 3. Servicios (10 total — datos en `src/data/content.ts`)

| # | Servicio |
| :- | :------- |
| 1 | Desarrollo de Software a Medida |
| 2 | Aplicaciones Web y Móviles |
| 3 | Sistemas Empresariales (ERP y CRM) |
| 4 | Inteligencia Artificial |
| 5 | Automatización de Procesos |
| 6 | Integración de APIs |
| 7 | Soluciones SaaS |
| 8 | Bases de Datos y Cloud Computing |
| 9 | Ciberseguridad |
| 10 | Soporte y Mantenimiento |

---

## 4. Stack del Proyecto Web

| Capa | Tecnología | Versión |
| :--- | :--------- | :------ |
| Framework | React | 19 |
| Lenguaje | TypeScript | ~6.0 |
| Build | Vite | 8 |
| Estilos | Tailwind CSS | 4 (Vite plugin) |
| Deploy | GitHub Pages | via GitHub Actions |
| Animaciones | CSS custom + canvas | — |

**Sin dependencias de UI** (no hay MUI, Shadcn, etc.) — todos los componentes son custom.

---

## 5. Estructura del Repositorio

```
zentrox-web/
├── .github/workflows/deploy.yml    # CI/CD: build + deploy a GitHub Pages en push a main
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── Navbar.tsx              # Header sticky, mobile menu, scroll style change
│   │   ├── Hero.tsx                # Hero section, canvas particles, PixelScene sunset
│   │   ├── Services.tsx            # Grid de 10 cards de servicios
│   │   ├── About.tsx               # Misión/Visión/Valores + stats KPIs
│   │   ├── Portfolio.tsx           # 4 proyectos showcase con PixelScene night
│   │   ├── Technologies.tsx        # Marquee infinito + grid de 6 categorías tech
│   │   ├── Contact.tsx             # Formulario con validación + mailto
│   │   ├── Footer.tsx              # Links, redes sociales, copyright dinámico
│   │   ├── PixelArt.tsx            # Renderer SVG de matrices de pixel art
│   │   ├── PixelScene.tsx          # Generador procedural de ciudad pixelada (canvas)
│   │   ├── Reveal.tsx              # Wrapper para animaciones scroll-triggered
│   │   └── SectionTitle.tsx        # Header reutilizable de sección (eyebrow+title+sub)
│   ├── data/
│   │   └── content.ts              # TODA la data: servicios, tech, proyectos, nav links
│   ├── hooks/
│   │   └── useReveal.ts            # IntersectionObserver hook → { ref, visible }
│   ├── index.css                   # Variables CSS, fuentes, animaciones custom
│   ├── main.tsx                    # Punto de entrada React
│   └── App.tsx                     # Composición de secciones (sin router)
├── index.html                      # HTML raíz, lang="es", carga Google Fonts
├── vite.config.ts                  # base: '/zentrox-web/' en build, '/' en dev
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── eslint.config.js                # ESLint flat config
├── package.json
└── CLAUDE.md                       # Este archivo
```

---

## 6. Arquitectura y Convenciones de Código

### Navegación

No hay React Router. El sitio es un SPA de scroll vertical con `id` en cada sección. Los links usan `href="#seccion"` y `scroll-behavior: smooth` en CSS.

IDs de sección: `#inicio`, `#servicios`, `#nosotros`, `#portafolio`, `#tecnologias`, `#contacto`

### Componentes

```typescript
// Patrón estándar
const MyComponent: FC = () => { ... }
const MyComponent: FC<Props> = ({ prop }) => { ... }

// Props con interface explícita
interface MyComponentProps {
  children?: ReactNode
  className?: string
  delay?: number
}
```

- Componentes funcionales con hooks, sin clases
- Tipado estricto — `noUnusedLocals`, `noUnusedParameters` habilitados
- Sin state management externo — solo `useState` / `useRef` locales

### Animaciones de scroll

Usar el componente `<Reveal>` para animar elementos al entrar al viewport:

```tsx
<Reveal delay={index * 100}>
  <article>...</article>
</Reveal>
```

`Reveal` usa `useReveal` hook que aplica IntersectionObserver y agrega `.visible` a la clase `.reveal`. La animación está definida en `index.css`.

### Pixel Art (íconos)

Los íconos se definen como matrices de caracteres en `src/data/content.ts` dentro del objeto `PIXEL_ICONS`. El componente `<PixelArt>` los renderiza como SVG con `shapeRendering="crispEdges"`.

Paleta de caracteres en matrices:
```
g → #ffd805 (gold)
o → #f49f20 (orange)
c → #ffe37c (cream)
a → #afafaf (gray)
w → #ffffff (white)
b → #000000 (black)
. → transparent
```

Para añadir un nuevo ícono, agregar la matriz a `PIXEL_ICONS` en `content.ts`.

### PixelScene (fondos procedurales)

`<PixelScene>` genera una ciudad pixel-art de forma determinista usando una semilla (`seed` prop). Las variantes son `'sunset'` (dorado) y `'night'` (oscuro). Resolución interna: 240×135px escalada con `imageRendering: pixelated`.

```tsx
<PixelScene variant="sunset" seed={42} className="w-full h-full" />
<PixelScene variant="night"  seed={project.id} className="..." />
```

### Datos de contenido

**Toda la data editable está en `src/data/content.ts`** — nunca hardcodear texto en componentes. Si hay que modificar servicios, proyectos, tech stack o links de navegación, editar solo ese archivo.

Exports principales:
- `COMPANY` — info de la empresa
- `PIXEL_ICONS` — matrices de íconos
- `SERVICES` — array de 10 servicios
- `TECHNOLOGIES` — array de 6 categorías con sus tecnologías
- `PROJECTS` — array de 4 proyectos de portafolio
- `NAV_LINKS` — array de links de navegación

### Estilos

- Tailwind utilities para layout, spacing, colores
- Clases custom en `index.css` para animaciones y efectos: `.scanlines`, `.pixel-float`, `.glitch-hover`, `.reveal`, `.marquee-track`, `.pixel-corners`, `.blink-cursor`
- Variables CSS `--color-*` para colores de marca
- Mobile-first siempre: breakpoints `md:` y `lg:` para tablet/desktop

---

## 7. Flujos de Desarrollo

### Comandos principales

```bash
npm install          # instalar dependencias
npm run dev          # servidor de desarrollo → http://localhost:5173
npm run build        # compilar → dist/ (TypeScript + Vite)
npm run lint         # ESLint
npm run preview      # previsualizar build de producción
```

### Build y deploy

El deploy a GitHub Pages es automático: cualquier push a `main` dispara `.github/workflows/deploy.yml` que ejecuta `npm ci && npm run build` y sube `dist/` a GitHub Pages.

El base path en producción es `/zentrox-web/` (configurado en `vite.config.ts`). En desarrollo es `/`.

**No usar `npm run deploy`** (script manual de gh-pages) — el CI/CD lo hace automáticamente.

### TypeScript estricto

El build falla si hay errores de tipo. Antes de hacer commit, verificar con `npm run build`. Los parámetros no utilizados y las importaciones sin uso causan error de compilación.

### Sin tests automatizados

No hay Vitest/Jest configurado. Las pruebas son manuales en el navegador.

---

## 8. Reglas para AI Assistants

1. **Colores**: Usar SOLO los 5 colores de la paleta oficial. Nunca inventar colores nuevos.
2. **Data**: Toda la data de contenido va en `src/data/content.ts`, no hardcodeada en JSX.
3. **Componentes**: Funcionales con TypeScript. Tipado explícito en props.
4. **Iconos**: Usar `PixelArt` + matrices en `PIXEL_ICONS`, no emojis ni librerías de íconos externas.
5. **Animaciones**: Usar `.reveal` vía `<Reveal>` para entradas. Usar clases custom de `index.css` para efectos retro.
6. **Fuentes**: `Press Start 2P` para títulos/marca, `Space Grotesk` para cuerpo. No añadir otras fuentes.
7. **Responsive**: Mobile-first. Layout en 1 col → 2 cols (md) → 3 cols (lg).
8. **Sin librerías nuevas**: No agregar componentes UI externos (MUI, Radix, etc.). Todo custom.
9. **Navegación**: Sin React Router. Solo anclas `href="#id"`.
10. **Build limpio**: `npm run build` debe pasar sin errores antes de hacer commit.

---

## 9. Historial reciente de commits

| Hash | Mensaje |
| :--- | :------ |
| b8edcc6 | Actualizar actions a Node 24 (deprecacion de Node 20) |
| 6331345 | Escenas pixel-art procedurales estilo lofi: skyline al atardecer en hero y ciudades nocturnas en portafolio |
| 55beb14 | Agregar script npm run deploy (gh-pages) |
| ca402fc | Sitio web oficial de Zentrox: React + TypeScript + Tailwind, estilo retro-arcade |

---

*Actualizado: Junio 2026 — Kevin Porras / Zentrox*
