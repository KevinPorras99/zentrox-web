import { useEffect, useRef } from 'react'
import type { FC } from 'react'

/**
 * Escena pixel-art procedural estilo lofi (skyline de ciudad) generada en canvas,
 * usando exclusivamente la paleta de Zentrox y sus tonos oscurecidos.
 * Determinística por semilla: la misma semilla siempre produce la misma ciudad.
 */

const W = 240
const H = 135

type RGB = readonly [number, number, number]

const hex = (h: string): RGB => [
  parseInt(h.slice(1, 3), 16),
  parseInt(h.slice(3, 5), 16),
  parseInt(h.slice(5, 7), 16),
]

// Degradado de cielo: negro → dorado (#ffd805) → crema (#ffe37c), tonos derivados de la marca
const SUNSET_SKY = [
  '#000000', '#100b02', '#241805', '#3a2608', '#57380b',
  '#7a4d0e', '#a8680f', '#d88614', '#f49f20', '#ffd805', '#ffe37c',
].map(hex)

const NIGHT_SKY = [
  '#000000', '#000000', '#0a0703', '#100b03', '#171005', '#1f1506', '#2a1c07',
].map(hex)

const GOLD = hex('#ffd805')
const ORANGE = hex('#f49f20')
const CREAM = hex('#ffe37c')
const WINDOW_DIM = hex('#57380b')
const BACK_BUILDING_SUNSET = hex('#1c1404')
const BACK_BUILDING_NIGHT = hex('#0d0a05')
const BLACK: RGB = [0, 0, 0]

/** PRNG determinístico (mulberry32) */
function mulberry32(seed: number): () => number {
  let a = seed >>> 0
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export type SceneVariant = 'sunset' | 'night'

function drawScene(canvas: HTMLCanvasElement, seed: number, variant: SceneVariant): void {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rnd = mulberry32(seed)
  const img = ctx.createImageData(W, H)
  const data = img.data

  const put = (x: number, y: number, c: RGB) => {
    if (x < 0 || x >= W || y < 0 || y >= H) return
    const i = (y * W + x) * 4
    data[i] = c[0]
    data[i + 1] = c[1]
    data[i + 2] = c[2]
    data[i + 3] = 255
  }

  const horizon = Math.floor(H * 0.66)
  const sky = variant === 'sunset' ? SUNSET_SKY : NIGHT_SKY

  // --- Cielo con dithering ordenado (matriz de Bayer 4×4, look pixel art clásico) ---
  const BAYER = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
  ]
  for (let y = 0; y < H; y++) {
    const t = Math.min(y / horizon, 1)
    const f = t * (sky.length - 1)
    const i = Math.floor(f)
    const frac = f - i
    for (let x = 0; x < W; x++) {
      const threshold = (BAYER[y % 4][x % 4] + 0.5) / 16
      const c = i < sky.length - 1 && frac > threshold ? sky[i + 1] : sky[i]
      put(x, y, c)
    }
  }

  // --- Sol (atardecer) o luna (noche) ---
  if (variant === 'sunset') {
    const cx = Math.floor(W * 0.72)
    const cy = horizon - 16
    const r = 15
    for (let y = cy - r; y <= cy + r; y++) {
      if (y > cy && (y - cy) % 3 === 0) continue // bandas retro en la mitad inferior
      if (y >= horizon) break
      for (let x = cx - r; x <= cx + r; x++) {
        const d = Math.hypot(x - cx, y - cy)
        if (d <= r) put(x, y, d < r * 0.55 ? CREAM : GOLD)
      }
    }
  } else {
    const cx = Math.floor(W * (0.2 + rnd() * 0.2))
    const cy = 22
    const r = 10
    for (let y = cy - r; y <= cy + r; y++) {
      for (let x = cx - r; x <= cx + r; x++) {
        const d = Math.hypot(x - cx, y - cy)
        if (d <= r) put(x, y, d < r * 0.4 || (x + y) % 7 === 0 ? GOLD : CREAM)
      }
    }
  }

  // --- Nubes pixeladas ---
  const cloudColors =
    variant === 'sunset' ? [hex('#a8680f'), hex('#d88614'), ORANGE] : [hex('#241805'), hex('#3a2608')]
  const cloudCount = 5 + Math.floor(rnd() * 3)
  for (let k = 0; k < cloudCount; k++) {
    const cy = Math.floor(5 + rnd() * horizon * 0.65)
    const cx = Math.floor(rnd() * W)
    const len = 18 + Math.floor(rnd() * 38)
    const rows = 2 + Math.floor(rnd() * 3)
    const c = cloudColors[Math.min(cloudColors.length - 1, Math.floor((cy / horizon) * cloudColors.length))]
    for (let ry = 0; ry < rows; ry++) {
      const inset = Math.floor(rnd() * 5) + ry * 2
      for (let x = cx + inset; x < cx + len - inset; x++) put(x, cy + ry, c)
    }
  }

  // --- Edificios de fondo (silueta tenue) ---
  const backColor = variant === 'sunset' ? BACK_BUILDING_SUNSET : BACK_BUILDING_NIGHT
  let x = -Math.floor(rnd() * 10)
  while (x < W) {
    const bw = 10 + Math.floor(rnd() * 22)
    const bh = 12 + Math.floor(rnd() * 28)
    const top = horizon - bh
    for (let bx = x; bx < x + bw && bx < W; bx++) {
      for (let by = top; by < H; by++) put(bx, by, backColor)
    }
    // ventanas tenues
    for (let wx = x + 2; wx < x + bw - 2; wx += 3) {
      for (let wy = top + 3; wy < horizon; wy += 4) {
        if (rnd() < 0.12) put(wx, wy, WINDOW_DIM)
      }
    }
    x += bw + 1
  }

  // --- Edificios frontales (silueta negra con ventanas doradas) ---
  x = -Math.floor(rnd() * 8)
  while (x < W) {
    const bw = 14 + Math.floor(rnd() * 26)
    const bh = 18 + Math.floor(rnd() * 40)
    const top = horizon - bh

    // antena con punta naranja
    if (rnd() < 0.4) {
      const ax = x + Math.floor(bw / 2)
      const ah = 4 + Math.floor(rnd() * 7)
      for (let ay = top - ah; ay < top; ay++) put(ax, ay, BLACK)
      put(ax, top - ah, ORANGE)
    }

    for (let bx = x; bx < x + bw && bx < W; bx++) {
      for (let by = top; by < H; by++) put(bx, by, BLACK)
    }

    // ventanas iluminadas
    const windowColors = [GOLD, ORANGE, CREAM, WINDOW_DIM, WINDOW_DIM]
    for (let wx = x + 2; wx < x + bw - 2; wx += 3) {
      for (let wy = top + 3; wy < H - 4; wy += 4) {
        if (rnd() < 0.28) {
          put(wx, wy, windowColors[Math.floor(rnd() * windowColors.length)])
        }
      }
    }
    x += bw + 2 + Math.floor(rnd() * 4)
  }

  ctx.putImageData(img, 0, 0)
}

export interface PixelSceneProps {
  seed?: number
  variant?: SceneVariant
  className?: string
}

const PixelScene: FC<PixelSceneProps> = ({ seed = 1, variant = 'sunset', className }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (canvasRef.current) drawScene(canvasRef.current, seed, variant)
  }, [seed, variant])

  return (
    <canvas
      ref={canvasRef}
      width={W}
      height={H}
      className={className}
      style={{ imageRendering: 'pixelated' }}
      aria-hidden="true"
    />
  )
}

export default PixelScene
