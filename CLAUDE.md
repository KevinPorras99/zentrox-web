# CLAUDE.md — Contexto del Proyecto Zentrox

Este archivo fue generado desde una sesión de Cowork para proporcionar contexto completo a Claude Code. Contiene toda la información sobre la empresa, identidad de marca, servicios, stack técnico y requerimientos del proyecto web.

---

## 1\. Sobre la Empresa

| Campo | Detalle |
| :---- | :---- |
| **Nombre** | Zentrox |
| **Tipo** | Empresa de Desarrollo de Software e Inteligencia Artificial |
| **Ubicación** | Alajuela, Costa Rica |
| **Correo** | [kevinporras9906@gmail.com](mailto:kevinporras9906@gmail.com) |
| **Teléfono** | \+506 8645-7832 |
| **Eslogan** | "Transformamos ideas en soluciones digitales innovadoras." |
| **Headline principal** | SOLUCIONES TECNOLÓGICAS INTELIGENTES |

---

## 2\. Identidad de Marca

### Paleta de colores (oficial)

Primary Gold:   \#ffd805   ← Color principal, textos destacados, CTAs

Orange Accent:  \#f49f20   ← Acentos, íconos, hover states

Light Cream:    \#ffe37c   ← Fondos secundarios, gradientes suaves

Gray:           \#afafaf   ← Textos secundarios, bordes, decoraciones

Black:          \#000000   ← Fondo principal, texto base

### Estilo visual

- **Estética:** Retro-arcade / 8-bit / pixel art — minimalista, profesional, corporativo  
- **Tipografía:** Retro pixelada (tipo arcade) para títulos/marca; sans-serif moderna para cuerpo de texto  
- **Tono:** Futurista pero con carácter retro-gamer, elegante, alto contraste  
- **Logo:** Isologo (símbolo \+ texto fusionados), estilo pixel art con patrón de mosaico detrás, fondo negro, dorado y naranja

### Assets generados (Canva)

- **Isologo guardado:** [https://www.canva.com/d/FOdHT3X6Vi2Fg\_3](https://www.canva.com/d/FOdHT3X6Vi2Fg_3)  
- **Post Instagram guardado:** [https://www.canva.com/d/p\_s\_ljKMEj5IYf](https://www.canva.com/d/p_s_ljKMEj5IYf)\_  
- **Banner HTML:** `zentrox_banner.html` (incluido en este proyecto)

---

## 3\. Servicios de la Empresa

| \# | Servicio | Descripción breve |
| :---- | :---- | :---- |
| 1 | Desarrollo de Software a Medida | Soluciones digitales hechas para cada negocio |
| 2 | Aplicaciones Web y Móviles | Experiencias digitales en cualquier dispositivo |
| 3 | Sistemas Empresariales (ERP y CRM) | Gestión inteligente de la empresa |
| 4 | Inteligencia Artificial | Automatiza y potencia decisiones con IA |
| 5 | Automatización de Procesos | Elimina tareas repetitivas y ahorra tiempo |
| 6 | Integración de APIs | Conecta sistemas y plataformas sin esfuerzo |
| 7 | Soluciones SaaS | Software escalable bajo modelo de suscripción |
| 8 | Bases de Datos y Cloud Computing | Información segura y disponible siempre |
| 9 | Ciberseguridad | Protección de datos y sistemas críticos |
| 10 | Soporte y Mantenimiento | Acompañamiento continuo post-entrega |

---

## 4\. Stack Técnico del Desarrollador (Kevin Porras)

Lenguajes:

  \- PHP 8, Python, JavaScript, TypeScript, Java, C++

Frameworks:

  \- Laravel 11 (backend principal)

  \- ReactJS (frontend)

  \- Bootstrap

Bases de datos:

  \- MySQL

  \- PostgreSQL

Auth & Pagos:

  \- Clerk Auth

  \- Stripe

  \- JWT

  \- Laravel Sanctum

BaaS / Cloud:

  \- Supabase (Postgres, Auth, Realtime, Storage)

  \- Microsoft Azure

  \- AWS (EC2, RDS)

  \- Netlify

DevOps & CI/CD:

  \- GitHub Actions

  \- Docker (básico)

  \- CI/CD Pipelines

  \- Linux CLI

Herramientas AI:

  \- Claude (Anthropic)

  \- ChatGPT (OpenAI)

  \- Gemini (Google)

Colaboración:

  \- Git, GitHub

  \- Azure DevOps (Boards & Repos)

  \- Trello

---

## 5\. Proyecto Web — Requerimientos

### Objetivo

Crear el sitio web oficial de Zentrox que refleje la identidad de marca retro-arcade profesional, con imágenes representativas, secciones interactivas y alto impacto visual.

### Stack elegido

Frontend: React \+ TypeScript

Estilos: Tailwind CSS (recomendado) o CSS Modules

Animaciones: Framer Motion o CSS animations

### Secciones requeridas

1. **Hero / Landing** — Headline principal, eslogan, CTA ("Contáctanos" / "Ver servicios"), animaciones pixel art  
2. **Servicios** — Cards interactivas para cada uno de los 10 servicios, con íconos estilo pixel  
3. **Sobre Nosotros** — Historia de la empresa, misión, visión  
4. **Portafolio / Proyectos** — Trabajos realizados  
5. **Tecnologías** — Stack que dominamos (logos/íconos animados)  
6. **Contacto** — Formulario de contacto, datos de la empresa  
7. **Footer** — Links, redes sociales, copyright Zentrox

### Guía de diseño para el código

/\* Colores — usar como variables CSS \*/

\--color-primary: \#ffd805;

\--color-accent: \#f49f20;

\--color-cream: \#ffe37c;

\--color-gray: \#afafaf;

\--color-bg: \#000000;

\--color-text: \#ffffff;

/\* Tipografía sugerida (Google Fonts) \*/

\--font-brand: 'Press Start 2P', monospace;   /\* títulos retro \*/

\--font-body: 'Inter' o 'Space Grotesk', sans-serif; /\* cuerpo \*/

### Comportamientos interactivos esperados

- Hover effects en cards de servicios (efecto pixel/glitch o iluminación dorada)  
- Animaciones de entrada al hacer scroll (fade-in, slide-up)  
- Cursor personalizado o partículas estilo pixel en el hero  
- Navbar sticky con cambio de estilo al hacer scroll  
- Formulario de contacto con validación y feedback visual

---

## 6\. Notas para Claude Code

- Respetar **estrictamente** la paleta de colores oficial (`#ffd805`, `#f49f20`, `#ffe37c`, `#afafaf`, `#000000`)  
- La tipografía de títulos debe ser pixel/retro — usar `Press Start 2P` de Google Fonts  
- El diseño es **mobile-first**, responsive  
- Preferir componentes funcionales con hooks en React  
- Usar TypeScript con tipado estricto  
- El archivo `zentrox_banner.html` incluido tiene el banner SVG de referencia visual  
- Las imágenes deben ser representativas de tech/AI/software con el estilo retro-arcade de la marca  
- Incluir `CLAUDE.md` actualizado en el repositorio para mantener contexto entre sesiones

---

*Generado por Claude Cowork — Sesión: Kevin Porras / Zentrox — Junio 2026*  
