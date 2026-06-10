/* ============ Contenido oficial de Zentrox ============ */

export const COMPANY = {
  name: 'Zentrox',
  slogan: 'Transformamos ideas en soluciones digitales innovadoras.',
  headline: 'SOLUCIONES TECNOLÓGICAS INTELIGENTES',
  location: 'Alajuela, Costa Rica',
  email: 'kevinporras9906@gmail.com',
  phone: '+506 8645-7832',
} as const

/* ---- Íconos pixel art (matrices 11×N, paleta oficial) ---- */

export const PIXEL_ICONS = {
  code: [
    '...........',
    '..g.....g..',
    '.g...o...g.',
    'g....o....g',
    'g...o.....g',
    'g...o.....g',
    '.g.o.....g.',
    '..g.....g..',
    '...........',
  ],
  devices: [
    'ggggggg....',
    'g.....g....',
    'g.ccc.g.ooo',
    'g.ccc.g.oco',
    'g.....g.oco',
    'ggggggg.oco',
    '...g....oco',
    '..ggg...ooo',
    '...........',
  ],
  chart: [
    '...........',
    '.......gg..',
    '.......gg..',
    '....oo.gg..',
    '....oo.gg..',
    '.aa.oo.gg..',
    '.aa.oo.gg..',
    '.aa.oo.gg..',
    'aaaaaaaaaaa',
  ],
  robot: [
    '.....o.....',
    '.....g.....',
    '.ggggggggg.',
    '.g.......g.',
    '.g.o...o.g.',
    '.g.......g.',
    '.g.ccccc.g.',
    '.ggggggggg.',
    '..a.....a..',
  ],
  gear: [
    '....ggg....',
    '.gg.ggg.gg.',
    '.ggggggggg.',
    '..ggg.ggg..',
    'gggg...gggg',
    'ggg..o..ggg',
    'gggg...gggg',
    '..ggg.ggg..',
    '.ggggggggg.',
    '.gg.ggg.gg.',
    '....ggg....',
  ],
  api: [
    'ggg........',
    'g.g........',
    'ggg........',
    '...oo......',
    '.....oo....',
    '.......oo..',
    '........ggg',
    '........g.g',
    '........ggg',
  ],
  cloud: [
    '...gggg....',
    '..gggggg...',
    '.gggggggg..',
    'gggggggggg.',
    '...........',
    '.....o.....',
    '....ooo....',
    '...ooooo...',
    '.....o.....',
    '.....o.....',
  ],
  database: [
    '..ggggggg..',
    '.ggggggggg.',
    '.g.......g.',
    '.g.......g.',
    '.gooooooog.',
    '.g.......g.',
    '.gooooooog.',
    '.g.......g.',
    '.ggggggggg.',
    '..ggggggg..',
  ],
  shield: [
    'ggggggggggg',
    'ggggggggggg',
    'ggggggggggg',
    'ggggggggogg',
    'gggggggoggg',
    'ggogggogggg',
    'gggogoggggg',
    '.ggggogggg.',
    '..ggggggg..',
    '...ggggg...',
    '....ggg....',
  ],
  headset: [
    '...........',
    '...ggggg...',
    '..g.....g..',
    '.g.......g.',
    'og.......go',
    'oo.......oo',
    'oo.......oo',
    '.........o.',
    '......ooo..',
  ],
  invader: [
    '..g.....g..',
    '...g...g...',
    '..ggggggg..',
    '.gg.ggg.gg.',
    'ggggggggggg',
    'g.ggggggg.g',
    'g.g.....g.g',
    '...gg.gg...',
  ],
} as const

export type PixelIconName = keyof typeof PIXEL_ICONS

/* ---- Servicios ---- */

export interface Service {
  id: number
  title: string
  description: string
  icon: PixelIconName
}

export const SERVICES: readonly Service[] = [
  { id: 1, title: 'Desarrollo de Software a Medida', description: 'Soluciones digitales hechas para cada negocio.', icon: 'code' },
  { id: 2, title: 'Aplicaciones Web y Móviles', description: 'Experiencias digitales en cualquier dispositivo.', icon: 'devices' },
  { id: 3, title: 'Sistemas Empresariales (ERP y CRM)', description: 'Gestión inteligente de la empresa.', icon: 'chart' },
  { id: 4, title: 'Inteligencia Artificial', description: 'Automatiza y potencia decisiones con IA.', icon: 'robot' },
  { id: 5, title: 'Automatización de Procesos', description: 'Elimina tareas repetitivas y ahorra tiempo.', icon: 'gear' },
  { id: 6, title: 'Integración de APIs', description: 'Conecta sistemas y plataformas sin esfuerzo.', icon: 'api' },
  { id: 7, title: 'Soluciones SaaS', description: 'Software escalable bajo modelo de suscripción.', icon: 'cloud' },
  { id: 8, title: 'Bases de Datos y Cloud Computing', description: 'Información segura y disponible siempre.', icon: 'database' },
  { id: 9, title: 'Ciberseguridad', description: 'Protección de datos y sistemas críticos.', icon: 'shield' },
  { id: 10, title: 'Soporte y Mantenimiento', description: 'Acompañamiento continuo post-entrega.', icon: 'headset' },
]

/* ---- Tecnologías ---- */

export interface TechCategory {
  category: string
  items: readonly string[]
}

export const TECHNOLOGIES: readonly TechCategory[] = [
  { category: 'Lenguajes', items: ['PHP 8', 'Python', 'JavaScript', 'TypeScript', 'Java', 'C++'] },
  { category: 'Frameworks', items: ['Laravel 11', 'ReactJS', 'Bootstrap', 'Tailwind CSS'] },
  { category: 'Bases de Datos', items: ['MySQL', 'PostgreSQL', 'Supabase'] },
  { category: 'Cloud & DevOps', items: ['AWS', 'Microsoft Azure', 'Docker', 'GitHub Actions', 'Netlify', 'Linux'] },
  { category: 'Auth & Pagos', items: ['Clerk Auth', 'Stripe', 'JWT', 'Laravel Sanctum'] },
  { category: 'Inteligencia Artificial', items: ['Claude (Anthropic)', 'ChatGPT (OpenAI)', 'Gemini (Google)'] },
]

export const TECH_MARQUEE: readonly string[] = TECHNOLOGIES.flatMap((t) => [...t.items])

/* ---- Portafolio ---- */

export interface Project {
  id: number
  title: string
  tag: string
  description: string
  stack: readonly string[]
  icon: PixelIconName
}

export const PROJECTS: readonly Project[] = [
  {
    id: 1,
    title: 'Sistema ERP Empresarial',
    tag: 'ERP / CRM',
    description: 'Plataforma de gestión integral: inventario, facturación electrónica y reportes en tiempo real para pymes costarricenses.',
    stack: ['Laravel 11', 'React', 'MySQL'],
    icon: 'chart',
  },
  {
    id: 2,
    title: 'Asistente Virtual con IA',
    tag: 'Inteligencia Artificial',
    description: 'Chatbot inteligente para atención al cliente 24/7, integrado con Claude y entrenado con la base de conocimiento del negocio.',
    stack: ['Python', 'Claude API', 'Supabase'],
    icon: 'robot',
  },
  {
    id: 3,
    title: 'Plataforma SaaS de Reservas',
    tag: 'SaaS',
    description: 'Software de reservas por suscripción con pagos en línea, recordatorios automáticos y panel administrativo.',
    stack: ['React', 'TypeScript', 'Stripe'],
    icon: 'cloud',
  },
  {
    id: 4,
    title: 'Integración de APIs Bancarias',
    tag: 'Integraciones',
    description: 'Conexión segura entre sistemas contables y pasarelas de pago con sincronización automática de transacciones.',
    stack: ['PHP 8', 'JWT', 'PostgreSQL'],
    icon: 'api',
  },
]

/* ---- Navegación ---- */

export interface NavLink {
  label: string
  href: string
}

export const NAV_LINKS: readonly NavLink[] = [
  { label: 'Inicio', href: '#inicio' },
  { label: 'Servicios', href: '#servicios' },
  { label: 'Nosotros', href: '#nosotros' },
  { label: 'Portafolio', href: '#portafolio' },
  { label: 'Tecnologías', href: '#tecnologias' },
  { label: 'Contacto', href: '#contacto' },
]
