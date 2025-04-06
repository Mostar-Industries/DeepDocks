import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"
import type { ShipmentData } from "@/components/ShipmentForm"
import { supabase } from "@/lib/supabase"

interface RankRequest extends ShipmentData {
  analysisDepth?: number
  criteria_pairwise?: number[][]
}

export async function POST(request: NextRequest) {
  try {
    const data: RankRequest = await request.json()

    // Default analysis depth if not provided
    const analysisDepth = data.analysisDepth || 3

    // Default pairwise matrix if not provided
    if (!data.criteria_pairwise) {
      // Create pairwise matrix based on urgency
      if (data.urgency === "express") {
        data.criteria_pairwise = [
          [1, 0.5, 2, 1],
          [2, 1, 3, 2],
          [0.5, 1 / 3, 1, 0.5],
          [1, 0.5, 2, 1],
        ]
      } else if (data.urgency === "rush") {
        data.criteria_pairwise = [
          [1, 0.25, 1, 0.5],
          [4, 1, 5, 3],
          [1, 0.2, 1, 0.5],
          [2, 1 / 3, 2, 1],
        ]
      } else {
        // Standard urgency
        data.criteria_pairwise = [
          [1, 2, 3, 4],
          [0.5, 1, 2, 3],
          [1 / 3, 0.5, 1, 2],
          [0.25, 1 / 3, 0.5, 1],
        ]
      }
    }

    // Fetch data from Supabase
    let supabaseData: any = null
    try {
      // Fetch forwarders
      const { data: forwarders, error: forwardersError } = await supabase.from("forwarders").select("*")
      if (forwardersError) throw forwardersError

      // Fetch routes
      const { data: routes, error: routesError } = await supabase.from("routes").select("*")
      if (routesError) throw routesError

      // Fetch rate cards
      const { data: rateCards, error: rateCardsError } = await supabase.from("rate_cards").select("*")
      if (rateCardsError) throw rateCardsError

      // Fetch forwarder services
      const { data: forwarderServices, error: servicesError } = await supabase.from("forwarder_services").select("*")
      if (servicesError) throw servicesError

      // Fetch performance analytics
      const { data: performanceAnalytics, error: analyticsError } = await supabase
        .from("performance_analytics")
        .select("*")
      if (analyticsError) throw analyticsError

      // Fetch shipments
      const { data: shipments, error: shipmentsError } = await supabase.from("shipments").select("*")
      if (shipmentsError) throw shipmentsError

      // Combine all data
      supabaseData = {
        forwarders,
        routes,
        rate_cards: rateCards,
        forwarder_services: forwarderServices,
        performance_analytics: performanceAnalytics,
        shipments,
      }
    } catch (supabaseError) {
      console.warn("Error fetching data from Supabase:", supabaseError)
      // Continue with null supabaseData - the core engine will use base data
    }

    // Add supabase data to the request
    const requestWithData = {
      ...data,
      supabase_data: supabaseData,
    }

    // Path to the Python runner script
    const pythonScriptPath = path.join(process.cwd(), "backend", "runner.py")

    // Spawn Python process
    const pythonProcess = spawn("python", [pythonScriptPath])

    // Send data to Python process
    pythonProcess.stdin.write(JSON.stringify(requestWithData))
    pythonProcess.stdin.end()

    // Collect output from Python process
    let outputData = ""
    let errorData = ""

    pythonProcess.stdout.on("data", (data) => {
      outputData += data.toString()
    })

    pythonProcess.stderr.on("data", (data) => {
      errorData += data.toString()
    })

    // Wait for Python process to complete
    const exitCode = await new Promise((resolve) => {
      pythonProcess.on("close", resolve)
    })

    // Check for errors
    if (exitCode !== 0) {
      console.error("Python process error:", errorData)
      return NextResponse.json({ error: "Failed to process ranking request", details: errorData }, { status: 500 })
    }

    try {
      // Parse the output as JSON
      const results = JSON.parse(outputData)

      // Save analysis to Supabase if user is authenticated
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser()

        if (user) {
          await supabase.from("user_analyses").insert({
            user_id: user.id,
            analysis_name: `${data.origin} to ${data.destination}`,
            forwarders: results.results,
            results: {
              topForwarder: results.results[0]?.name,
              score: results.results[0]?.score,
              weights: results.weights,
            },
            parameters: data,
          })
        }
      } catch (saveError) {
        console.error("Error saving analysis:", saveError)
        // Continue even if saving fails
      }

      return NextResponse.json(results)
    } catch (parseError) {
      console.error("Error parsing Python output:", parseError)
      console.error("Raw output:", outputData)
      return NextResponse.json({ error: "Failed to parse results", details: parseError.message }, { status: 500 })
    }
  } catch (error) {
    console.error("Error processing rank request:", error)
    return NextResponse.json({ error: "Failed to process ranking request" }, { status: 500 })
  }
}

// Mock function to generate results - used as fallback if Python process fails
function generateMockResults(data: RankRequest) {
  // Create base forwarders with different characteristics
  const forwarders = [
    {
      id: "f1",
      name: "AfricaLogistics",
      baseCost: 1200,
      baseTime: 14,
      baseReliability: 0.85,
      hasTracking: true,
    },
    {
      id: "f2",
      name: "GlobalFreight",
      baseCost: 950,
      baseTime: 18,
      baseReliability: 0.78,
      hasTracking: false,
    },
    {
      id: "f3",
      name: "ExpressShip",
      baseCost: 1450,
      baseTime: 10,
      baseReliability: 0.92,
      hasTracking: true,
    },
    {
      id: "f4",
      name: "TransAfrica",
      baseCost: 1100,
      baseTime: 15,
      baseReliability: 0.82,
      hasTracking: true,
    },
    {
      id: "f5",
      name: "FastCargo",
      baseCost: 1350,
      baseTime: 12,
      baseReliability: 0.88,
      hasTracking: false,
    },
  ]

  // Adjust costs based on weight and value
  const weightFactor = data.weight / 1000
  const valueFactor = data.value ? data.value / 10000 : 1

  // Calculate actual values for each forwarder
  const results = forwarders.map((forwarder) => {
    // Calculate cost based on weight and value
    const cost = forwarder.baseCost * (0.8 + weightFactor * 0.4) * (0.9 + valueFactor * 0.2)

    // Calculate delivery time based on urgency
    let deliveryTime = forwarder.baseTime
    if (data.urgency === "express") {
      deliveryTime = forwarder.baseTime * 0.8
    } else if (data.urgency === "rush") {
      deliveryTime = forwarder.baseTime * 0.6
    }

    // Adjust reliability based on cargo type
    let reliability = forwarder.baseReliability
    if (data.fragile) {
      reliability *= 0.95
    }
    if (data.hazardous) {
      reliability *= 0.9
    }
    if (data.perishable) {
      reliability *= 0.92
    }

    // Calculate normalized factors (0-1 scale, lower is better for cost and time)
    const costFactor = (cost - 900) / 1000 // Normalize to 0-1 range
    const timeFactor = deliveryTime / 20 // Normalize to 0-1 range
    const reliabilityFactor = reliability // Already 0-1

    // Calculate weights based on urgency
    let weights = {
      cost: 0.4,
      time: 0.3,
      reliability: 0.2,
      tracking: 0.1,
    }

    if (data.urgency === "express") {
      weights = {
        cost: 0.2,
        time: 0.5,
        reliability: 0.2,
        tracking: 0.1,
      }
    } else if (data.urgency === "rush") {
      weights = {
        cost: 0.1,
        time: 0.6,
        reliability: 0.2,
        tracking: 0.1,
      }
    }

    // Calculate TOPSIS score (simplified)
    // Higher is better, so invert cost and time factors
    const score =
      weights.cost * (1 - costFactor) +
      weights.time * (1 - timeFactor) +
      weights.reliability * reliabilityFactor +
      weights.tracking * (forwarder.hasTracking ? 1 : 0)

    return {
      id: forwarder.id,
      name: forwarder.name,
      score,
      cost: Math.round(cost),
      deliveryTime: Math.round(deliveryTime),
      reliability: Math.round(reliability * 100),
      hasTracking: forwarder.hasTracking,
      costFactor,
      timeFactor,
      reliabilityFactor,
    }
  })

  // Sort by score (descending)
  results.sort((a, b) => b.score - a.score)

  // Assign ranks
  results.forEach((result, index) => {
    result.rank = index + 1
  })

  // Add criterion contributions
  results.forEach((result) => {
    const weights =
      data.urgency === "express"
        ? { cost: 0.2, time: 0.5, reliability: 0.2, tracking: 0.1 }
        : data.urgency === "rush"
          ? { cost: 0.1, time: 0.6, reliability: 0.2, tracking: 0.1 }
          : { cost: 0.4, time: 0.3, reliability: 0.2, tracking: 0.1 }

    result.criterionContributions = [
      (weights.cost * (1 - result.costFactor)) / result.score,
      (weights.time * (1 - result.timeFactor)) / result.score,
      (weights.reliability * result.reliabilityFactor) / result.score,
      (weights.tracking * (result.hasTracking ? 1 : 0)) / result.score,
    ]

    result.commentary = generateForwarderCommentary(result, data)
  })

  // Add sensitivity analysis
  results.forEach((result) => {
    result.sensitivityAnalysis = {
      weightChanges: ["Cost: +10%", "Cost: -10%", "Time: +10%", "Time: -10%", "Reliability: +10%", "Reliability: -10%"],
      scoreChanges: calculateScoreChanges(result, data.urgency),
    }
  })

  // Generate commentary
  const commentary = generateCommentary(results, data)

  // Return the response
  return {
    results,
    weights:
      data.urgency === "express"
        ? { cost: 0.2, time: 0.5, reliability: 0.2, tracking: 0.1 }
        : data.urgency === "rush"
          ? { cost: 0.1, time: 0.6, reliability: 0.2, tracking: 0.1 }
          : { cost: 0.4, time: 0.3, reliability: 0.2, tracking: 0.1 },
    commentary,
    analysisDepth: 5,
  }
}

// Helper function to calculate score change percentage
function calculateScoreChanges(result: any, urgency: string) {
  const weights =
    urgency === "express"
      ? { cost: 0.2, time: 0.5, reliability: 0.2, tracking: 0.1 }
      : urgency === "rush"
        ? { cost: 0.1, time: 0.6, reliability: 0.2, tracking: 0.1 }
        : { cost: 0.4, time: 0.3, reliability: 0.2, tracking: 0.1 }

  const originalScore = result.score

  // Cost +10%
  const costPlusScore =
    weights.cost * 1.1 * (1 - result.costFactor) +
    weights.time * (1 - result.timeFactor) +
    weights.reliability * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  // Cost -10%
  const costMinusScore =
    weights.cost * 0.9 * (1 - result.costFactor) +
    weights.time * (1 - result.timeFactor) +
    weights.reliability * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  // Time +10%
  const timePlusScore =
    weights.cost * (1 - result.costFactor) +
    weights.time * 1.1 * (1 - result.timeFactor) +
    weights.reliability * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  // Time -10%
  const timeMinusScore =
    weights.cost * (1 - result.costFactor) +
    weights.time * 0.9 * (1 - result.timeFactor) +
    weights.reliability * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  // Reliability +10%
  const reliabilityPlusScore =
    weights.cost * (1 - result.costFactor) +
    weights.time * (1 - result.timeFactor) +
    weights.reliability * 1.1 * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  // Reliability -10%
  const reliabilityMinusScore =
    weights.cost * (1 - result.costFactor) +
    weights.time * (1 - result.timeFactor) +
    weights.reliability * 0.9 * result.reliabilityFactor +
    weights.tracking * (result.hasTracking ? 1 : 0)

  return [
    ((costPlusScore - originalScore) / originalScore) * 100,
    ((costMinusScore - originalScore) / originalScore) * 100,
    ((timePlusScore - originalScore) / originalScore) * 100,
    ((timeMinusScore - originalScore) / originalScore) * 100,
    ((reliabilityPlusScore - originalScore) / originalScore) * 100,
    ((reliabilityMinusScore - originalScore) / originalScore) * 100,
  ]
}

// Generate commentary for a specific forwarder
function generateForwarderCommentary(result: any, data: RankRequest) {
  const commentaries = [
    `${result.name} offers a balanced approach with ${result.reliability}% reliability and ${result.deliveryTime} day delivery.`,
    `${result.name} is particularly strong in ${result.costFactor < 0.4 ? "cost efficiency" : result.timeFactor < 0.4 ? "delivery speed" : "reliability"}.`,
    `For shipments from ${data.origin} to ${data.destination}, ${result.name} has a proven track record.`,
    `${result.name} ${result.hasTracking ? "provides real-time tracking capabilities" : "does not offer tracking services"} for this route.`,
    `${result.name} is ${result.rank === 1 ? "the top-ranked option" : `ranked #${result.rank}`} based on your shipment requirements.`,
  ]

  // Select 2-3 random commentaries
  const selectedCommentaries = []
  const indices = new Set<number>()

  while (indices.size < Math.min(3, commentaries.length)) {
    indices.add(Math.floor(Math.random() * commentaries.length))
  }

  indices.forEach((index) => {
    selectedCommentaries.push(commentaries[index])
  })

  return selectedCommentaries.join(" ")
}

// Generate overall commentary
function generateCommentary(results: any[], data: RankRequest) {
  const topResult = results[0]
  const runnerUp = results[1]

  let commentary = `Based on your shipment requirements from ${data.origin} to ${data.destination}, ${topResult.name} is the recommended logistics forwarder with a score of ${topResult.score.toFixed(3)}. `

  // Add urgency-specific commentary
  if (data.urgency === "rush") {
    commentary += `For your rush shipment, ${topResult.name} offers the fastest delivery time of ${topResult.deliveryTime} days. `
  } else if (data.urgency === "express") {
    commentary += `For your express shipment, ${topResult.name} provides a good balance of speed and reliability. `
  } else {
    commentary += `For your standard shipment, ${topResult.name} offers the best overall value. `
  }

  // Add comparison with runner-up
  if (runnerUp) {
    commentary += `Compared to ${runnerUp.name} (ranked #2), ${topResult.name} ${
      topResult.cost < runnerUp.cost
        ? `is $${runnerUp.cost - topResult.cost} cheaper`
        : `costs $${topResult.cost - runnerUp.cost} more`
    } and ${
      topResult.deliveryTime < runnerUp.deliveryTime
        ? `is ${runnerUp.deliveryTime - topResult.deliveryTime} days faster`
        : `takes ${topResult.deliveryTime - runnerUp.deliveryTime} more days`
    }.`
  }

  // Add special cargo commentary
  if (data.fragile || data.hazardous || data.perishable) {
    const specialTypes = []
    if (data.fragile) specialTypes.push("fragile")
    if (data.hazardous) specialTypes.push("hazardous")
    if (data.perishable) specialTypes.push("perishable")

    commentary += ` For your ${specialTypes.join(" and ")} cargo, reliability is particularly important, and ${topResult.name} offers ${topResult.reliability}% reliability.`
  }

  return commentary
}

