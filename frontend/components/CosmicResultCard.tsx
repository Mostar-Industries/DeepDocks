"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Rocket,
  DollarSign,
  Clock,
  Shield,
  Truck,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface ForwarderResult {
  id: string
  name: string
  score: number
  rank: number
  cost: number
  deliveryTime: number
  reliability: number
  hasTracking: boolean
  costFactor: number
  timeFactor: number
  reliabilityFactor: number
  criterionContributions?: number[]
  commentary?: string
}

interface CosmicResultCardProps {
  result: ForwarderResult
  isRecommended: boolean
  onSelect: (forwarderId: string) => void
}

export default function CosmicResultCard({
  result,
  isRecommended = false,
  onSelect = () => {},
}: CosmicResultCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [isHovering, setIsHovering] = useState(false)

  // Check if result is undefined or null
  if (!result) {
    return (
      <Card className="border rounded-lg overflow-hidden shadow-md bg-black/40 p-6 text-center border-gray-800">
        <h3 className="font-medium text-gray-500">Forwarder Data Unavailable</h3>
        <p className="text-sm text-gray-400 mt-2">The requested forwarder information could not be loaded.</p>
      </Card>
    )
  }

  // Safely destructure with default values for all properties
  const {
    id = "unknown",
    name = "Unknown Forwarder",
    score = 0,
    rank = 0,
    cost = 0,
    deliveryTime = 0,
    reliability = 0,
    hasTracking = false,
    costFactor = 0,
    timeFactor = 0,
    reliabilityFactor = 0,
    commentary,
  } = result

  // Calculate factor bars (values between 0-100 for display)
  const costBar = 100 - costFactor * 100 // Inverse for cost (lower is better)
  const timeBar = 100 - timeFactor * 100 // Inverse for time (lower is better)
  const reliabilityBar = reliabilityFactor * 100

  // Fun facts about the forwarder
  const funFacts = [
    `${name} once delivered a package so fast that it arrived before it was sent!`,
    `${name}'s delivery vehicles run on pure cosmic energy and good vibes.`,
    `${name}'s tracking system is so precise it can locate a needle in a galaxy-sized haystack.`,
    `${name} employs a team of quantum physicists to bend space-time for faster deliveries.`,
    `${name}'s reliability score is higher than the chance of finding a four-leaf clover.`,
  ]

  const randomFunFact = funFacts[Math.floor(Math.random() * funFacts.length)]

  // Get emoji based on rank
  const getRankEmoji = () => {
    if (rank === 1) return "🥇"
    if (rank === 2) return "🥈"
    if (rank === 3) return "🥉"
    return "🏅"
  }

  // Get color based on score
  const getScoreColor = () => {
    if (score > 0.8) return "text-green-400"
    if (score > 0.6) return "text-blue-400"
    if (score > 0.4) return "text-yellow-400"
    return "text-red-400"
  }

  // Card variants for animation
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        delay: rank * 0.1,
      },
    },
    hover: {
      y: -10,
      transition: { duration: 0.3 },
    },
  }

  // Content variants for animation
  const contentVariants = {
    hidden: { opacity: 0, height: 0 },
    visible: {
      opacity: 1,
      height: "auto",
      transition: { duration: 0.3 },
    },
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={isRecommended ? {} : "hover"}
      className={`card-3d ${isRecommended ? "float" : ""}`}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <Card
        className={`overflow-hidden transition-all duration-300 backdrop-blur-sm
          ${
            isRecommended
              ? "border-green-500 bg-black/60 neon-border-green"
              : "border-gray-800 bg-black/40 hover:border-blue-500/50"
          }`}
      >
        {/* Header */}
        <div
          className={`px-4 py-3 relative overflow-hidden
            ${isRecommended ? "bg-green-950/40" : "bg-gray-950/40"}`}
        >
          {/* Background particles */}
          {isRecommended && (
            <div className="absolute inset-0 overflow-hidden">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 rounded-full bg-green-400"
                  initial={{
                    x: Math.random() * 100 + "%",
                    y: Math.random() * 100 + "%",
                    opacity: Math.random() * 0.5 + 0.3,
                  }}
                  animate={{
                    y: [Math.random() * 100 + "%", Math.random() * 100 + "%"],
                    opacity: [Math.random() * 0.5 + 0.3, Math.random() * 0.2 + 0.1],
                  }}
                  transition={{
                    duration: Math.random() * 3 + 2,
                    repeat: Number.POSITIVE_INFINITY,
                    repeatType: "reverse",
                  }}
                />
              ))}
            </div>
          )}

          <div className="relative z-10">
            <div className="flex justify-between items-center">
              <h3 className={`font-bold text-lg ${isRecommended ? "neon-text-green" : ""}`}>{name}</h3>
              {isRecommended && (
                <Badge className="bg-green-600 text-white text-xs font-semibold px-2 py-1 rounded-full">
                  <Sparkles className="h-3 w-3 mr-1" />
                  TOP PICK
                </Badge>
              )}
            </div>
            <div className="text-sm mt-1 flex items-center gap-2">
              <span className="flex items-center">
                {getRankEmoji()} Rank: {rank}
              </span>
              <span className="w-1 h-1 rounded-full bg-gray-500"></span>
              <span className={`flex items-center ${getScoreColor()}`}>Score: {score.toFixed(3)}</span>
            </div>
          </div>
        </div>

        {/* Body */}
        <CardContent className="p-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-black/30 rounded-lg p-3 backdrop-blur-sm">
              <span className="text-gray-400 text-sm flex items-center">
                <DollarSign className="h-4 w-4 mr-1 text-blue-400" /> Cost
              </span>
              <div className="text-xl font-semibold flex items-center">
                <span>${cost.toLocaleString()}</span>
                {isHovering && (
                  <motion.div initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} className="ml-2">
                    <DollarSign className="h-4 w-4 text-blue-400" />
                  </motion.div>
                )}
              </div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 backdrop-blur-sm">
              <span className="text-gray-400 text-sm flex items-center">
                <Clock className="h-4 w-4 mr-1 text-pink-400" /> Delivery Time
              </span>
              <div className="text-xl font-semibold flex items-center">
                <span>{deliveryTime} days</span>
                {isHovering && (
                  <motion.div initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} className="ml-2">
                    <Rocket className="h-4 w-4 text-pink-400" />
                  </motion.div>
                )}
              </div>
            </div>
          </div>

          {/* Factors Visualization */}
          <div className="space-y-3 my-4">
            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span className="flex items-center">
                  <DollarSign className="h-3 w-3 mr-1 text-blue-400" />
                  Cost Efficiency
                </span>
                <span>{costBar.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${costBar}%` }}
                  transition={{ duration: 1, delay: rank * 0.1 }}
                  className="bg-blue-600 h-2 rounded-full"
                ></motion.div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span className="flex items-center">
                  <Clock className="h-3 w-3 mr-1 text-pink-400" />
                  Time Efficiency
                </span>
                <span>{timeBar.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${timeBar}%` }}
                  transition={{ duration: 1, delay: rank * 0.1 + 0.2 }}
                  className="bg-pink-600 h-2 rounded-full"
                ></motion.div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span className="flex items-center">
                  <Shield className="h-3 w-3 mr-1 text-green-400" />
                  Reliability
                </span>
                <span>{reliabilityBar.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${reliabilityBar}%` }}
                  transition={{ duration: 1, delay: rank * 0.1 + 0.4 }}
                  className="bg-green-500 h-2 rounded-full"
                ></motion.div>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="flex items-center mt-4 text-sm">
            <div className="mr-4">
              <span className={`inline-flex items-center ${hasTracking ? "text-green-400" : "text-gray-500"}`}>
                {hasTracking ? <CheckCircle className="h-4 w-4 mr-1" /> : <XCircle className="h-4 w-4 mr-1" />}
                Tracking
              </span>
            </div>
            <div>
              <span className="inline-flex items-center text-gray-400">
                <Truck className="h-4 w-4 mr-1 text-blue-400" />
                {deliveryTime} days
              </span>
            </div>
          </div>

          {/* Expandable content */}
          <div className="mt-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              className="w-full flex items-center justify-center text-xs text-gray-400 hover:text-white hover:bg-gray-800"
            >
              {expanded ? (
                <>
                  <span>Show Less</span>
                  <ChevronUp className="h-4 w-4 ml-1" />
                </>
              ) : (
                <>
                  <span>Show More</span>
                  <ChevronDown className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>

            <AnimatePresence>
              {expanded && (
                <motion.div
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="mt-4 overflow-hidden"
                >
                  <div className="bg-black/30 rounded-lg p-3 backdrop-blur-sm">
                    <h4 className="text-sm font-medium text-blue-400 mb-2">Cosmic Intelligence Report</h4>
                    <p className="text-sm text-gray-300">{commentary || randomFunFact}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Action Button */}
          <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} className="mt-4">
            <Button
              onClick={() => onSelect(id)}
              className={`w-full py-2 px-4 rounded-md text-sm font-medium relative overflow-hidden
                ${
                  isRecommended
                    ? "bg-green-600 text-white hover:bg-green-700"
                    : "bg-gray-800 text-gray-200 hover:bg-gray-700"
                }`}
            >
              <span className="relative z-10">{isRecommended ? "Select Recommended" : "Select This Option"}</span>

              {/* Button animation */}
              {isRecommended && (
                <motion.div
                  className="absolute inset-0 bg-green-500"
                  initial={{ x: "-100%" }}
                  animate={{ x: "200%" }}
                  transition={{
                    repeat: Number.POSITIVE_INFINITY,
                    duration: 2,
                    ease: "linear",
                  }}
                  style={{ opacity: 0.3 }}
                />
              )}
            </Button>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

