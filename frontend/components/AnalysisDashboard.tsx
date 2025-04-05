"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { InfoIcon, AlertCircle, TrendingUp, BarChart3, PieChart, Truck, Clock, DollarSign } from "lucide-react"
import ResultCard from "./ResultCard"
import type { ShipmentData } from "./ShipmentForm"

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

interface AnalysisDashboardProps {
  shipmentData: ShipmentData | null
  onReset: () => void
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ shipmentData, onReset }) => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>("basic")

  useEffect(() => {
    if (shipmentData) {
      fetchAnalysisResults(shipmentData)
    }
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

  // Render loading state
  if (loading) {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-1/3" />
            <Skeleton className="h-4 w-2/3" />
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Skeleton className="h-[300px]" />
              <Skeleton className="h-[300px]" />
              <Skeleton className="h-[300px]" />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Render error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to retrieve analysis results: {error}
          <div className="mt-4">
            <Button onClick={() => shipmentData && fetchAnalysisResults(shipmentData)}>Retry</Button>
            <Button variant="outline" className="ml-2" onClick={onReset}>
              Reset Form
            </Button>
          </div>
        </AlertDescription>
      </Alert>
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

  return (
    <div className="space-y-6">
      {/* Header with summary */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl">Logistics Forwarder Analysis</CardTitle>
              <CardDescription>
                Analysis based on{" "}
                {Object.entries(weights)
                  .map(([key, value]) => `${key} (${(value * 100).toFixed(0)}%)`)
                  .join(", ")}
              </CardDescription>
            </div>
            <Button onClick={onReset}>New Analysis</Button>
          </div>
        </CardHeader>
        <CardContent>
          <Alert>
            <InfoIcon className="h-4 w-4" />
            <AlertTitle>Analysis Summary</AlertTitle>
            <AlertDescription className="mt-2">
              <p className="mb-2">{commentary}</p>
              {topResult && runnerUp && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="bg-green-600">
                      RECOMMENDED
                    </Badge>
                    <span className="font-medium">{topResult.name}</span>
                    <span className="text-sm text-muted-foreground">Score: {topResult.score.toFixed(3)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">RUNNER UP</Badge>
                    <span className="font-medium">{runnerUp.name}</span>
                    <span className="text-sm text-muted-foreground">Score: {runnerUp.score.toFixed(3)}</span>
                  </div>
                </div>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Tabs for basic and advanced views */}
      <Tabs defaultValue="basic" value={activeTab} onValueChange={handleTabChange}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="basic">Basic Calculation</TabsTrigger>
          <TabsTrigger value="advanced">Advanced Analysis</TabsTrigger>
        </TabsList>

        {/* Basic view with forwarder cards */}
        <TabsContent value="basic" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result) => (
              <ResultCard
                key={result.id}
                result={result}
                isRecommended={result.rank === 1}
                onSelect={() => console.log(`Selected forwarder: ${result.name}`)}
              />
            ))}
          </div>
        </TabsContent>

        {/* Advanced view with detailed analysis */}
        <TabsContent value="advanced" className="space-y-6">
          {/* Top forwarder detailed card */}
          {topResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="h-5 w-5" />
                  {topResult.name} - Detailed Analysis
                </CardTitle>
                <CardDescription>Comprehensive analysis of the recommended forwarder</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left column - Key metrics */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Key Performance Metrics</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                          <DollarSign className="h-4 w-4" /> Cost
                        </div>
                        <div className="text-2xl font-bold">${topResult.cost.toLocaleString()}</div>
                      </div>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                          <Clock className="h-4 w-4" /> Delivery Time
                        </div>
                        <div className="text-2xl font-bold">{topResult.deliveryTime} days</div>
                      </div>
                    </div>

                    {/* Factor bars */}
                    <div className="space-y-3 mt-6">
                      <h4 className="text-sm font-medium">Performance Factors</h4>
                      <div>
                        <div className="flex justify-between text-xs text-muted-foreground mb-1">
                          <span>Cost Efficiency</span>
                          <span>{(100 - topResult.costFactor * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${100 - topResult.costFactor * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs text-muted-foreground mb-1">
                          <span>Time Efficiency</span>
                          <span>{(100 - topResult.timeFactor * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${100 - topResult.timeFactor * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs text-muted-foreground mb-1">
                          <span>Reliability</span>
                          <span>{(topResult.reliabilityFactor * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-yellow-500 h-2 rounded-full"
                            style={{ width: `${topResult.reliabilityFactor * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right column - Commentary and sensitivity */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Analysis Commentary</h3>
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm">{topResult.commentary || "No detailed commentary available."}</p>
                    </div>

                    {topResult.sensitivityAnalysis && (
                      <div className="mt-6">
                        <h4 className="text-sm font-medium mb-2">Sensitivity Analysis</h4>
                        <div className="bg-muted p-4 rounded-lg">
                          <p className="text-xs text-muted-foreground mb-2">
                            How the score would change with different criteria weights:
                          </p>
                          <div className="space-y-2">
                            {topResult.sensitivityAnalysis.weightChanges.map((change, index) => (
                              <div key={index} className="flex justify-between items-center text-xs">
                                <span>{change}</span>
                                <div className="flex items-center">
                                  <span
                                    className={
                                      topResult.sensitivityAnalysis!.scoreChanges[index] > 0
                                        ? "text-green-500"
                                        : "text-red-500"
                                    }
                                  >
                                    {topResult.sensitivityAnalysis!.scoreChanges[index] > 0 ? "+" : ""}
                                    {topResult.sensitivityAnalysis!.scoreChanges[index].toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Criterion contributions chart */}
          {topResult?.criterionContributions && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Decision Factor Analysis
                </CardTitle>
                <CardDescription>Breakdown of how each factor contributed to the final recommendation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Factor contribution bars */}
                    <div className="col-span-2 space-y-3">
                      <h4 className="text-sm font-medium">Factor Contributions</h4>
                      {["Cost", "Delivery Time", "Reliability", "Tracking"].map((factor, index) => {
                        if (!topResult.criterionContributions?.[index] && index > 2) return null
                        const contribution = topResult.criterionContributions?.[index] || 0
                        return (
                          <div key={factor}>
                            <div className="flex justify-between text-xs text-muted-foreground mb-1">
                              <span>{factor}</span>
                              <span>{(contribution * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-muted rounded-full h-3">
                              <div
                                className={`h-3 rounded-full ${
                                  index === 0
                                    ? "bg-blue-600"
                                    : index === 1
                                      ? "bg-purple-600"
                                      : index === 2
                                        ? "bg-yellow-500"
                                        : "bg-green-600"
                                }`}
                                style={{ width: `${contribution * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* Donut chart placeholder - in a real implementation, this would use Chart.js or D3 */}
                    <div className="flex flex-col items-center justify-center">
                      <h4 className="text-sm font-medium mb-2">Factor Distribution</h4>
                      <div className="relative w-32 h-32">
                        <PieChart className="w-32 h-32 text-muted-foreground" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-sm font-medium">{topResult.score.toFixed(2)}</span>
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">Overall Score</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comparison with alternatives */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Comparative Analysis
              </CardTitle>
              <CardDescription>How the recommended forwarder compares to alternatives</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-3 text-sm font-medium">Forwarder</th>
                      <th className="text-right py-2 px-3 text-sm font-medium">Score</th>
                      <th className="text-right py-2 px-3 text-sm font-medium">Cost</th>
                      <th className="text-right py-2 px-3 text-sm font-medium">Time</th>
                      <th className="text-right py-2 px-3 text-sm font-medium">Reliability</th>
                      <th className="text-center py-2 px-3 text-sm font-medium">Tracking</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
                      <tr key={result.id} className="border-b hover:bg-muted/50">
                        <td className="py-2 px-3 text-sm">
                          <div className="flex items-center gap-2">
                            {result.rank === 1 && (
                              <Badge variant="default" className="bg-green-600">
                                #1
                              </Badge>
                            )}
                            {result.name}
                          </div>
                        </td>
                        <td className="text-right py-2 px-3 text-sm font-medium">{result.score.toFixed(3)}</td>
                        <td className="text-right py-2 px-3 text-sm">${result.cost.toLocaleString()}</td>
                        <td className="text-right py-2 px-3 text-sm">{result.deliveryTime} days</td>
                        <td className="text-right py-2 px-3 text-sm">{(result.reliabilityFactor * 100).toFixed(0)}%</td>
                        <td className="text-center py-2 px-3 text-sm">
                          {result.hasTracking ? (
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-800">
                              ✓
                            </span>
                          ) : (
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-100 text-red-800">
                              ✗
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AnalysisDashboard

