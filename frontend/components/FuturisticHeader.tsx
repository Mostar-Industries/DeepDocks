"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Sparkles, Rocket, Zap, Globe, BarChart3 } from "lucide-react"

interface FuturisticHeaderProps {
  title: string
  subtitle?: string
}

export default function FuturisticHeader({ title, subtitle }: FuturisticHeaderProps) {
  const [randomTip, setRandomTip] = useState("")

  const funTips = [
    "Shipping to Mars takes approximately 7 months. We're working on it!",
    "If we stacked all your packages, they'd reach the moon... eventually.",
    "Our AI can predict shipping times better than your weather app predicts rain.",
    "Packages don't teleport... yet. We're still researching quantum shipping.",
    "The fastest recorded delivery was 0.2 seconds. It was an email.",
    "Our logistics robots dream of electric sheep during maintenance.",
    "If logistics were a sport, we'd have more gold medals than a dragon's hoard.",
    "We've calculated 7,429 routes to get your package there. We picked the best one.",
  ]

  useEffect(() => {
    setRandomTip(funTips[Math.floor(Math.random() * funTips.length)])

    const interval = setInterval(() => {
      setRandomTip(funTips[Math.floor(Math.random() * funTips.length)])
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative overflow-hidden rounded-xl bg-black/40 backdrop-blur-sm p-6 mb-8">
      <div className="absolute top-0 left-0 w-full h-full opacity-10">
        <div className="absolute top-0 left-0 w-full h-full star-field"></div>
      </div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-2">
          <motion.div
            initial={{ rotate: 0 }}
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
            className="text-blue-400"
          >
            <Sparkles size={28} className="text-blue-400" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold tracking-tight neon-text"
          >
            {title}
          </motion.h1>
        </div>

        {subtitle && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-gray-400 max-w-3xl"
          >
            {subtitle}
          </motion.p>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-4 flex items-center gap-2 text-sm text-blue-300 italic"
        >
          <Zap size={14} className="text-blue-400 pulse" />
          <span className="opacity-80">{randomTip}</span>
        </motion.div>

        <div className="absolute top-4 right-4 flex gap-3">
          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center cursor-pointer tooltip"
            data-tooltip="Global Logistics Network"
          >
            <Globe size={18} className="text-blue-400" />
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center cursor-pointer tooltip"
            data-tooltip="Launch Mission Control"
          >
            <Rocket size={18} className="text-pink-400" />
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center cursor-pointer tooltip"
            data-tooltip="Analytics Dashboard"
          >
            <BarChart3 size={18} className="text-green-400" />
          </motion.div>
        </div>
      </div>
    </div>
  )
}

