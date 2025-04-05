"use client"

import { useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { Sparkles } from "lucide-react"

interface HolographicVisualizationProps {
  data: {
    name: string
    value: number
    color: string
  }[]
  title: string
  height?: number
}

export default function HolographicVisualization({ data, title, height = 300 }: HolographicVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()

    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr

    ctx.scale(dpr, dpr)

    // Animation variables
    let animationFrameId: number
    let rotation = 0

    // Draw function
    const draw = () => {
      // Clear canvas
      ctx.clearRect(0, 0, rect.width, rect.height)

      // Calculate total value for percentage
      const total = data.reduce((sum, item) => sum + item.value, 0)

      // Draw 3D bars
      const barWidth = (rect.width - 80) / data.length
      const maxBarHeight = rect.height - 80

      // Draw grid
      ctx.strokeStyle = "rgba(255, 255, 255, 0.05)"
      ctx.lineWidth = 0.5

      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = rect.height - 40 - (i * maxBarHeight) / 5
        ctx.beginPath()
        ctx.moveTo(40, y)
        ctx.lineTo(rect.width - 40, y)
        ctx.stroke()
      }

      // Draw bars
      data.forEach((item, index) => {
        const x = 40 + index * barWidth
        const normalizedValue = item.value / Math.max(...data.map((d) => d.value))
        const barHeight = normalizedValue * maxBarHeight

        // 3D effect - side
        ctx.fillStyle = `rgba(${hexToRgb(item.color)}, 0.3)`
        ctx.beginPath()
        ctx.moveTo(x + barWidth - 10, rect.height - 40)
        ctx.lineTo(x + barWidth - 10, rect.height - 40 - barHeight)
        ctx.lineTo(x + barWidth, rect.height - 40 - barHeight + 10)
        ctx.lineTo(x + barWidth, rect.height - 40 + 10)
        ctx.closePath()
        ctx.fill()

        // 3D effect - top
        ctx.fillStyle = `rgba(${hexToRgb(item.color)}, 0.5)`
        ctx.beginPath()
        ctx.moveTo(x, rect.height - 40 - barHeight)
        ctx.lineTo(x + barWidth - 10, rect.height - 40 - barHeight)
        ctx.lineTo(x + barWidth, rect.height - 40 - barHeight + 10)
        ctx.lineTo(x + 10, rect.height - 40 - barHeight + 10)
        ctx.closePath()
        ctx.fill()

        // Main bar
        ctx.fillStyle = `rgba(${hexToRgb(item.color)}, 0.8)`
        ctx.fillRect(x, rect.height - 40 - barHeight, barWidth - 10, barHeight)

        // Glow effect
        const gradient = ctx.createLinearGradient(x, rect.height - 40 - barHeight, x, rect.height - 40)
        gradient.addColorStop(0, `rgba(${hexToRgb(item.color)}, 0.8)`)
        gradient.addColorStop(1, `rgba(${hexToRgb(item.color)}, 0.1)`)

        ctx.fillStyle = gradient
        ctx.globalAlpha = 0.5 + Math.sin(rotation + index) * 0.2
        ctx.fillRect(x, rect.height - 40 - barHeight, barWidth - 10, barHeight)
        ctx.globalAlpha = 1

        // Label
        ctx.fillStyle = "#fff"
        ctx.font = "10px sans-serif"
        ctx.textAlign = "center"
        ctx.fillText(item.name, x + (barWidth - 10) / 2, rect.height - 25)

        // Value
        ctx.fillStyle = `rgba(${hexToRgb(item.color)}, 1)`
        ctx.font = "12px sans-serif"
        ctx.textAlign = "center"
        ctx.fillText(
          `${Math.round((item.value / total) * 100)}%`,
          x + (barWidth - 10) / 2,
          rect.height - 40 - barHeight - 10,
        )

        // Particle effect
        const particleCount = Math.floor(normalizedValue * 5) + 1
        for (let i = 0; i < particleCount; i++) {
          const particleX = x + Math.random() * (barWidth - 10)
          const particleY = rect.height - 40 - Math.random() * barHeight
          const particleSize = Math.random() * 2 + 1

          ctx.fillStyle = `rgba(${hexToRgb(item.color)}, ${Math.random() * 0.5 + 0.5})`
          ctx.beginPath()
          ctx.arc(particleX, particleY, particleSize, 0, Math.PI * 2)
          ctx.fill()
        }
      })

      // Update rotation for animation
      rotation += 0.01

      // Request next frame
      animationFrameId = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      cancelAnimationFrame(animationFrameId)
    }
  }, [data])

  // Helper function to convert hex to rgb
  function hexToRgb(hex: string): string {
    // Remove # if present
    hex = hex.replace("#", "")

    // Parse hex values
    const r = Number.parseInt(hex.substring(0, 2), 16)
    const g = Number.parseInt(hex.substring(2, 4), 16)
    const b = Number.parseInt(hex.substring(4, 6), 16)

    return `${r}, ${g}, ${b}`
  }

  return (
    <div className="relative">
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-400" />
          <h3 className="font-medium text-sm neon-text">{title}</h3>
        </div>
        <motion.div
          className="text-xs text-blue-300 bg-blue-950/30 px-2 py-1 rounded-full"
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
        >
          HOLOGRAPHIC
        </motion.div>
      </div>

      <div className="relative holographic rounded-lg overflow-hidden bg-black/40 backdrop-blur-sm">
        <canvas ref={canvasRef} className="w-full" style={{ height: `${height}px` }} />

        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-0 w-full h-full opacity-50 star-field"></div>
          <div className="absolute top-0 left-0 w-full h-20 bg-gradient-to-b from-black/40 to-transparent"></div>
          <div className="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-black/40 to-transparent"></div>
        </div>
      </div>
    </div>
  )
}

