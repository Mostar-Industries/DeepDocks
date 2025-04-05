"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Rocket,
  BarChart3,
  Sparkles,
  Globe,
  Zap,
  AlertCircle,
  Info,
  Lightbulb,
  DollarSign,
  Clock,
  Shield,
  XCircle,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { ShipmentData } from "./ShipmentForm"
import CosmicResultCard from "./CosmicResultCard"
import HolographicVisualization from "./HolographicVisualization"
import FuturisticHeader from "./FuturisticHeader"

// Types for the analysis results
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
  sensitivityAnalysis?: {
    weightChanges: string[]
    scoreChanges: number[]
  }
}

interface AnalysisResult {
  results: ForwarderResult[]
  weights: {
    cost: number
    time: number
    reliability: number
    tracking: number
  }
  commentary: string
  analysisDepth: number
}

interface CosmicAnalysisDashboardProps {
  shipmentData: ShipmentData | null
  onReset: () => void
}

export default function CosmicAnalysisDashboard({ shipmentData, onReset }: CosmicAnalysisDashboardProps) {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>("basic")
  const [selectedForwarder, setSelectedForwarder] = useState<string | null>(null)
  const [showFunFact, setShowFunFact] = useState<boolean>(false)

  // Fun facts about logistics
  const funFacts = [
    "The word 'logistics' comes from the Greek word 'logistikos', meaning 'skilled in calculating'!",
    "The largest cargo ship can carry over 20,000 shipping containers at once!",
    "If all the shipping containers in the world were lined up end to end, they would circle the Earth more than twice!",
    "The fastest cargo plane can travel at speeds over 900 km/h!",
    "The global logistics industry is worth over $5 trillion annually!",
    "The average shipping container travels about 100,000 miles per year!",
    "The first shipping container was invented in 1956 by Malcolm McLean!",
    "About 90% of world trade is carried by the international shipping industry!",
    "The largest logistics hub in the world is in Hong Kong!",
    "The term 'supply chain' was first used in the 1980s!",
  ]

  // Random fun fact
  const [funFact, setFunFact] = useState<string>(funFacts[Math.floor(Math.random() * funFacts.length)])

  useEffect(() => {
    if (shipmentData) {
      fetchAnalysisResults(shipmentData)
    }

    // Show fun fact every 15 seconds
    const funFactInterval = setInterval(() => {
      setShowFunFact(true)
      setFunFact(funFacts[Math.floor(Math.random() * funFacts.length)])

      // Hide after 5 seconds
      setTimeout(() => {
        setShowFunFact(false)
      }, 5000)
    }, 15000)

    return () => clearInterval(funFactInterval)
  }, [shipmentData])

  const fetchAnalysisResults = async (data: ShipmentData) => {
    setLoading(true)
    setError(null)

    try {
      // Determine analysis depth based on active tab
      const analysisDepth = activeTab === "advanced" ? 5 : 3

      // Prepare the request payload
      const payload = {
        ...data,
        analysisDepth,
      }

      // Call the backend API
      const response = await fetch("/api/rank", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      setAnalysisResult(result)

      // Set the top result as selected by default
      if (result.results && result.results.length > 0) {
        setSelectedForwarder(result.results[0].id)
      }
    } catch (err) {
      console.error("Error fetching analysis results:", err)
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setLoading(false)
    }
  }

  // Handle tab change
  const handleTabChange = (value: string) => {
    setActiveTab(value)
    if (shipmentData && value === "advanced" && analysisResult?.analysisDepth !== 5) {
      // Refetch with higher analysis depth for advanced view
      fetchAnalysisResults(shipmentData)
    }
  }

  // Handle forwarder selection
  const handleSelectForwarder = (forwarderId: string) => {
    setSelectedForwarder(forwarderId)
  }

  // Render loading state
  if (loading) {
    return (
      <div className="space-y-8">
        <FuturisticHeader
          title="Calculating Optimal Routes"
          subtitle="Our quantum computers are analyzing millions of possible logistics pathways..."
        />

        <div className="relative">
          <Card className="border-blue-500/30 bg-black/40 backdrop-blur-sm overflow-hidden">
            <CardContent className="p-8">
              <div className="flex flex-col items-center justify-center min-h-[300px]">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                  className="relative"
                >
                  <Globe className="h-16 w-16 text-blue-400 opacity-30" />
                  <motion.div
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
                  >
                    <Sparkles className="h-8 w-8 text-blue-400" />
                  </motion.div>
                </motion.div>

                <motion.h3
                  className="mt-6 text-xl font-bold neon-text"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
                >
                  Calculating Cosmic Logistics
                </motion.h3>

                <div className="mt-4 max-w-md">
                  <motion.div
                    className="w-full h-2 bg-gray-800 rounded-full overflow-hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    <motion.div
                      className="h-full bg-blue-500"
                      initial={{ width: "0%" }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 3, repeat: Number.POSITIVE_INFINITY }}
                    />
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="mt-6 text-center text-sm text-gray-400"
                  >
                    <p className="mb-2">
                      Analyzing {shipmentData?.origin} to {shipmentData?.destination} route options...
                    </p>
                    <p>Calculating optimal cost-time-reliability balance...</p>
                  </motion.div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full bg-blue-400"
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
        </div>
      </div>
    )
  }

  // Render error state
  if (error) {
    return (
      <div className="space-y-8">
        <FuturisticHeader
          title="System Alert"
          subtitle="We've encountered a cosmic disturbance in the logistics matrix."
        />

        <Alert variant="destructive" className="bg-red-950/40 border-red-500/50">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-red-950 rounded-full">
              <AlertCircle className="h-6 w-6 text-red-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-red-400">Mission Critical Error</h3>
              <p className="mt-2 text-gray-300">Failed to retrieve analysis results: {error}</p>
              <div className="mt-4 flex gap-3">
                <Button
                  onClick={() => shipmentData && fetchAnalysisResults(shipmentData)}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  Retry Mission
                </Button>
                <Button
                  variant="outline"
                  className="border-red-500/30 text-red-400 hover:bg-red-950/30"
                  onClick={onReset}
                >
                  Abort Mission
                </Button>
              </div>
            </div>
          </div>
        </Alert>
      </div>
    )
  }

  // If no analysis result yet, show empty state
  if (!analysisResult) {
    return null
  }

  // Extract data for visualization
  const { results, weights, commentary } = analysisResult
  const topResult = results.find((r) => r.rank === 1)
  const runnerUp = results.find((r) => r.rank === 2)

  // Get selected forwarder details
  const selectedForwarderData = results.find((r) => r.id === selectedForwarder) || topResult

  // Prepare data for visualizations
  const weightData = [
    { name: "Cost", value: weights.cost, color: "#3b82f6" },
    { name: "Time", value: weights.time, color: "#ec4899" },
    { name: "Reliability", value: weights.reliability, color: "#10b981" },
    { name: "Tracking", value: weights.tracking, color: "#f59e0b" },
  ]

  const forwarderComparisonData = results.slice(0, 3).map((r) => ({
    name: r.name,
    value: r.score,
    color: r.rank === 1 ? "#10b981" : r.rank === 2 ? "#3b82f6" : "#ec4899",
  }))

  // Simplify commentary for 5-year-old
  const simplifyCommentary = (text: string) => {
    // Replace complex terms
    let simplified = text
      .replace(/logistics forwarder/gi, "space delivery team")
      .replace(/reliability/gi, "trustworthiness")
      .replace(/optimal/gi, "best")
      .replace(/efficiency/gi, "goodness")
      .replace(/criteria/gi, "super important things")
      .replace(/analysis/gi, "space check")
      .replace(/performance/gi, "awesomeness")
      .replace(/recommendation/gi, "super choice")
      .replace(/evaluation/gi, "checking")
      .replace(/assessment/gi, "looking at")
      .replace(/requirements/gi, "needs")
      .replace(/specifications/gi, "special needs")
      .replace(/configuration/gi, "setup")
      .replace(/parameters/gi, "magic numbers")
      .replace(/algorithm/gi, "magic math")
      .replace(/calculation/gi, "space math")
      .replace(/computation/gi, "number crunching")
      .replace(/optimization/gi, "making super good")

    // Simplify sentences
    simplified = simplified.replace(/(\. )/g, ". 😊 ").replace(/(! )/g, "! 🚀 ").replace(/(\? )/g, "? 🤔 ")

    return simplified
  }

  return (
    <div className="space-y-6 relative">
      {/* Fun fact popup */}
      <AnimatePresence>
        {showFunFact && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.9 }}
            className="fixed bottom-8 right-8 z-50 max-w-sm"
          >
            <Card className="border-blue-500/30 bg-black/80 backdrop-blur-md overflow-hidden">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-950/50 rounded-full">
                    <Lightbulb className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-blue-400">Cosmic Fun Fact!</h4>
                    <p className="mt-1 text-sm text-gray-300">{funFact}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header with summary */}
      <FuturisticHeader
        title="Cosmic Logistics Command Center"
        subtitle="Your shipment has been analyzed by our quantum logistics intelligence system"
      />

      <Card className="border-blue-500/30 bg-black/40 backdrop-blur-sm overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-950/30 rounded-full">
              <Info className="h-6 w-6 text-blue-400" />
            </div>

            <div className="flex-1">
              <h3 className="text-lg font-bold neon-text">Mission Briefing</h3>
              <motion.p
                className="mt-2 text-gray-300"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                {simplifyCommentary(commentary)}
              </motion.p>

              {topResult && runnerUp && (
                <motion.div
                  className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <Card className="bg-green-950/20 border-green-500/30">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="bg-green-600 text-white">
                          <Rocket className="h-3 w-3 mr-1" />
                          BEST CHOICE
                        </Badge>
                        <span className="font-medium neon-text-green">{topResult.name}</span>
                        <span className="text-sm text-green-400">Score: {topResult.score.toFixed(3)}</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-blue-950/20 border-blue-500/30">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="border-blue-500/50 text-blue-400">
                          RUNNER UP
                        </Badge>
                        <span className="font-medium">{runnerUp.name}</span>
                        <span className="text-sm text-blue-400">Score: {runnerUp.score.toFixed(3)}</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs for basic and advanced views */}
      <Tabs defaultValue="basic" value={activeTab} onValueChange={handleTabChange} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 p-1 bg-black/40 backdrop-blur-sm border border-gray-800 rounded-lg">
          <TabsTrigger
            value="basic"
            className="data-[state=active]:bg-blue-950/50 data-[state=active]:text-blue-400 data-[state=active]:neon-text"
          >
            <Rocket className="h-4 w-4 mr-2" />
            <span>Basic Mission</span>
          </TabsTrigger>
          <TabsTrigger
            value="advanced"
            className="data-[state=active]:bg-pink-950/50 data-[state=active]:text-pink-400 data-[state=active]:neon-text-pink"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            <span>Advanced Analytics</span>
          </TabsTrigger>
        </TabsList>

        {/* Basic view with forwarder cards */}
        <TabsContent value="basic" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((result) => (
              <CosmicResultCard
                key={result.id}
                result={result}
                isRecommended={result.rank === 1}
                onSelect={handleSelectForwarder}
              />
            ))}
          </div>

          <div className="flex justify-center mt-8">
            <Button
              onClick={onReset}
              variant="outline"
              className="border-blue-500/30 text-blue-400 hover:bg-blue-950/30"
            >
              <Rocket className="h-4 w-4 mr-2" />
              <span>Start New Mission</span>
            </Button>
          </div>
        </TabsContent>

        {/* Advanced view with detailed analysis */}
        <TabsContent value="advanced" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left column - Selected forwarder */}
            <div className="lg:col-span-2 space-y-6">
              {selectedForwarderData && (
                <Card className="border-pink-500/30 bg-black/40 backdrop-blur-sm overflow-hidden">
                  <div
                    className={`px-4 py-3 ${selectedForwarderData.rank === 1 ? "bg-green-950/40" : "bg-gray-950/40"}`}
                  >
                    <div className="flex justify-between items-center">
                      <h3 className={`font-bold text-lg ${selectedForwarderData.rank === 1 ? "neon-text-green" : ""}`}>
                        {selectedForwarderData.name} - Detailed Analysis
                      </h3>
                      {selectedForwarderData.rank === 1 && (
                        <Badge className="bg-green-600 text-white text-xs font-semibold px-2 py-1 rounded-full">
                          <Sparkles className="h-3 w-3 mr-1" />
                          TOP PICK
                        </Badge>
                      )}
                    </div>
                  </div>

                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Left column - Key metrics */}
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-black/30 rounded-lg p-3 backdrop-blur-sm">
                            <span className="text-gray-400 text-sm flex items-center">
                              <DollarSign className="h-4 w-4 mr-1 text-blue-400" /> Cost
                            </span>
                            <div className="text-xl font-semibold">${selectedForwarderData.cost.toLocaleString()}</div>
                          </div>
                          <div className="bg-black/30 rounded-lg p-3 backdrop-blur-sm">
                            <span className="text-gray-400 text-sm flex items-center">
                              <Clock className="h-4 w-4 mr-1 text-pink-400" /> Delivery Time
                            </span>
                            <div className="text-xl font-semibold">{selectedForwarderData.deliveryTime} days</div>
                          </div>
                        </div>

                        {/* Factor bars */}
                        <div className="space-y-3 mt-4">
                          <h4 className="text-sm font-medium text-gray-300">Performance Factors</h4>
                          <div>
                            <div className="flex justify-between text-xs text-gray-400 mb-1">
                              <span className="flex items-center">
                                <DollarSign className="h-3 w-3 mr-1 text-blue-400" />
                                Cost Efficiency
                              </span>
                              <span>{(100 - selectedForwarderData.costFactor * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${100 - selectedForwarderData.costFactor * 100}%` }}
                                transition={{ duration: 1 }}
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
                              <span>{(100 - selectedForwarderData.timeFactor * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${100 - selectedForwarderData.timeFactor * 100}%` }}
                                transition={{ duration: 1, delay: 0.2 }}
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
                              <span>{(selectedForwarderData.reliabilityFactor * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${selectedForwarderData.reliabilityFactor * 100}%` }}
                                transition={{ duration: 1, delay: 0.4 }}
                                className="bg-green-500 h-2 rounded-full"
                              ></motion.div>
                            </div>
                          </div>
                        </div>

                        {/* Features */}
                        <div className="mt-4 p-4 bg-black/30 rounded-lg backdrop-blur-sm">
                          <h4 className="text-sm font-medium text-gray-300 mb-3">Special Features</h4>
                          <div className="grid grid-cols-2 gap-3">
                            <div
                              className={`p-3 rounded-lg ${selectedForwarderData.hasTracking ? "bg-green-950/30 border border-green-500/30" : "bg-gray-900/50"}`}
                            >
                              <div className="flex items-center">
                                {selectedForwarderData.hasTracking ? (
                                  <Sparkles className="h-4 w-4 text-green-400 mr-2" />
                                ) : (
                                  <XCircle className="h-4 w-4 text-gray-500 mr-2" />
                                )}
                                <span
                                  className={`text-sm ${selectedForwarderData.hasTracking ? "text-green-400" : "text-gray-500"}`}
                                >
                                  Tracking System
                                </span>
                              </div>
                            </div>

                            <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-500/30">
                              <div className="flex items-center">
                                <Zap className="h-4 w-4 text-blue-400 mr-2" />
                                <span className="text-sm text-blue-400">
                                  {selectedForwarderData.deliveryTime} Day Delivery
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Right column - Commentary and sensitivity */}
                      <div className="space-y-4">
                        <div className="bg-black/30 rounded-lg p-4 backdrop-blur-sm border border-pink-500/20">
                          <h4 className="text-sm font-medium text-pink-400 mb-2">Cosmic Intelligence Report</h4>
                          <p className="text-sm text-gray-300">
                            {selectedForwarderData.commentary ||
                              `${selectedForwarderData.name} is ${selectedForwarderData.rank === 1 ? "the top choice" : `ranked #${selectedForwarderData.rank}`} for your shipment from ${shipmentData?.origin} to ${shipmentData?.destination}. They offer a ${selectedForwarderData.costFactor < 0.4 ? "very competitive" : selectedForwarderData.costFactor < 0.6 ? "reasonable" : "premium"} price point with ${selectedForwarderData.reliabilityFactor > 0.8 ? "excellent" : selectedForwarderData.reliabilityFactor > 0.6 ? "good" : "average"} reliability.`}
                          </p>
                        </div>

                        {selectedForwarderData.sensitivityAnalysis && (
                          <div className="bg-black/30 rounded-lg p-4 backdrop-blur-sm border border-blue-500/20">
                            <h4 className="text-sm font-medium text-blue-400 mb-2">Sensitivity Analysis</h4>
                            <p className="text-xs text-gray-400 mb-3">
                              How the score would change with different criteria weights:
                            </p>
                            <div className="space-y-2">
                              {selectedForwarderData.sensitivityAnalysis.weightChanges.map((change, index) => (
                                <div key={index} className="flex justify-between items-center text-xs">
                                  <span>{change}</span>
                                  <div className="flex items-center">
                                    <span
                                      className={
                                        selectedForwarderData.sensitivityAnalysis!.scoreChanges[index] > 0
                                          ? "text-green-400"
                                          : "text-red-400"
                                      }
                                    >
                                      {selectedForwarderData.sensitivityAnalysis!.scoreChanges[index] > 0 ? "+" : ""}
                                      {selectedForwarderData.sensitivityAnalysis!.scoreChanges[index].toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Criterion contributions */}
                        {selectedForwarderData.criterionContributions && (
                          <div className="bg-black/30 rounded-lg p-4 backdrop-blur-sm border border-green-500/20">
                            <h4 className="text-sm font-medium text-green-400 mb-2">Decision Factors</h4>
                            <p className="text-xs text-gray-400 mb-3">
                              How each factor contributed to the final score:
                            </p>
                            <div className="space-y-2">
                              {["Cost", "Time", "Reliability", "Tracking"].map((factor, index) => {
                                if (!selectedForwarderData.criterionContributions?.[index] && index > 2) return null
                                const contribution = selectedForwarderData.criterionContributions?.[index] || 0
                                return (
                                  <div key={factor}>
                                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                                      <span>{factor}</span>
                                      <span>Женско{(contribution * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-900 rounded-full h-2 overflow-hidden">
                                      <div
                                        className={`h-2 rounded-full ${
                                          index === 0
                                            ? "bg-blue-600"
                                            : index === 1
                                              ? "bg-pink-600"
                                              : index === 2
                                                ? "bg-green-500"
                                                : "bg-yellow-500"
                                        }`}
                                        style={{ width: `${contribution * 100}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Comparison table */}
              <Card className="border-blue-500/30 bg-black/40 backdrop-blur-sm overflow-hidden">
                <div className="px-4 py-3 bg-blue-950/40">
                  <h3 className="font-bold text-lg neon-text">Cosmic Fleet Comparison</h3>
                </div>

                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="border-b border-gray-800">
                          <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Forwarder</th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Score</th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Cost</th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Time</th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Reliability</th>
                          <th className="text-center py-3 px-4 text-sm font-medium text-gray-400">Tracking</th>
                          <th className="text-center py-3 px-4 text-sm font-medium text-gray-400">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.map((result) => (
                          <tr
                            key={result.id}
                            className={`border-b border-gray-800 hover:bg-blue-950/20 transition-colors duration-200 ${
                              selectedForwarder === result.id ? "bg-blue-950/30" : ""
                            }`}
                          >
                            <td className="py-3 px-4 text-sm">
                              <div className="flex items-center gap-2">
                                {result.rank === 1 && (
                                  <Badge variant="default" className="bg-green-600 text-white">
                                    #1
                                  </Badge>
                                )}
                                {result.name}
                              </div>
                            </td>
                            <td className="text-right py-3 px-4 text-sm font-medium">
                              <span
                                className={
                                  result.score > 0.8
                                    ? "text-green-400"
                                    : result.score > 0.6
                                      ? "text-blue-400"
                                      : result.score > 0.4
                                        ? "text-yellow-400"
                                        : "text-red-400"
                                }
                              >
                                {result.score.toFixed(3)}
                              </span>
                            </td>
                            <td className="text-right py-3 px-4 text-sm">${result.cost.toLocaleString()}</td>
                            <td className="text-right py-3 px-4 text-sm">{result.deliveryTime} days</td>
                            <td className="text-right py-3 px-4 text-sm">
                              {(result.reliabilityFactor * 100).toFixed(0)}%
                            </td>
                            <td className="text-center py-3 px-4 text-sm">
                              {result.hasTracking ? (
                                <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-950/50 text-green-400">
                                  ✓
                                </span>
                              ) : (
                                <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-950/50 text-red-400">
                                  ✗
                                </span>
                              )}
                            </td>
                            <td className="text-center py-3 px-4 text-sm">
                              <Button
                                size="sm"
                                variant={selectedForwarder === result.id ? "default" : "outline"}
                                className={
                                  selectedForwarder === result.id
                                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                                    : "border-blue-500/30 text-blue-400 hover:bg-blue-950/30"
                                }
                                onClick={() => handleSelectForwarder(result.id)}
                              >
                                {selectedForwarder === result.id ? "Selected" : "Select"}
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right column - Visualizations */}
            <div className="space-y-6">
              {/* Weight distribution */}
              <HolographicVisualization data={weightData} title="Decision Criteria Importance" height={250} />

              {/* Forwarder comparison */}
              <HolographicVisualization data={forwarderComparisonData} title="Top Forwarders Comparison" height={250} />

              {/* Mission details */}
              <Card className="border-pink-500/30 bg-black/40 backdrop-blur-sm overflow-hidden">
                <div className="px-4 py-3 bg-pink-950/40">
                  <h3 className="font-bold text-lg neon-text-pink">Mission Details</h3>
                </div>

                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Origin:</span>
                      <span className="text-sm font-medium">{shipmentData?.origin}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Destination:</span>
                      <span className="text-sm font-medium">{shipmentData?.destination}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Cargo Weight:</span>
                      <span className="text-sm font-medium">{shipmentData?.weight} kg</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Cargo Value:</span>
                      <span className="text-sm font-medium">${shipmentData?.value}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Cargo Type:</span>
                      <span className="text-sm font-medium">{shipmentData?.cargoType}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Urgency:</span>
                      <Badge
                        className={
                          shipmentData?.urgency === "rush"
                            ? "bg-green-600"
                            : shipmentData?.urgency === "express"
                              ? "bg-pink-600"
                              : "bg-blue-600"
                        }
                      >
                        {shipmentData?.urgency === "rush"
                          ? "Warp Speed"
                          : shipmentData?.urgency === "express"
                            ? "Hyperdrive"
                            : "Cruise Control"}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Special Handling:</span>
                      <div className="flex gap-2">
                        {shipmentData?.fragile && (
                          <Badge variant="outline" className="border-blue-500/50 text-blue-400">
                            Fragile
                          </Badge>
                        )}
                        {shipmentData?.hazardous && (
                          <Badge variant="outline" className="border-pink-500/50 text-pink-400">
                            Hazardous
                          </Badge>
                        )}
                        {shipmentData?.perishable && (
                          <Badge variant="outline" className="border-green-500/50 text-green-400">
                            Perishable
                          </Badge>
                        )}
                        {!shipmentData?.fragile && !shipmentData?.hazardous && !shipmentData?.perishable && (
                          <span className="text-sm font-medium">None</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <Button
                      onClick={onReset}
                      variant="outline"
                      className="w-full border-pink-500/30 text-pink-400 hover:bg-pink-950/30"
                    >
                      <Rocket className="h-4 w-4 mr-2" />
                      <span>Start New Mission</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

