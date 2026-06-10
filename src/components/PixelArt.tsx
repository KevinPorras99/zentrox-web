import type { FC } from 'react'

/**
 * Mapa de caracteres → colores oficiales de Zentrox.
 * '.' = transparente
 */
const PALETTE: Record<string, string> = {
  g: '#ffd805', // Primary Gold
  o: '#f49f20', // Orange Accent
  c: '#ffe37c', // Light Cream
  a: '#afafaf', // Gray
  w: '#ffffff', // White
  b: '#000000', // Black
}

export interface PixelArtProps {
  /** Filas de la matriz; cada carácter es un píxel */
  matrix: readonly string[]
  /** Tamaño en px de cada píxel renderizado */
  size?: number
  className?: string
  label?: string
}

/** Renderiza una matriz de caracteres como arte pixel en SVG (crisp edges). */
const PixelArt: FC<PixelArtProps> = ({ matrix, size = 4, className, label }) => {
  const rows = matrix.length
  const cols = matrix[0]?.length ?? 0

  return (
    <svg
      viewBox={`0 0 ${cols} ${rows}`}
      width={cols * size}
      height={rows * size}
      shapeRendering="crispEdges"
      className={className}
      role={label ? 'img' : 'presentation'}
      aria-label={label}
    >
      {matrix.flatMap((row, y) =>
        Array.from(row).map((ch, x) => {
          const fill = PALETTE[ch]
          if (!fill) return null
          return <rect key={`${x}-${y}`} x={x} y={y} width={1} height={1} fill={fill} />
        }),
      )}
    </svg>
  )
}

export default PixelArt
