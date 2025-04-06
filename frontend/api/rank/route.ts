import { type NextRequest, NextResponse } from "next/server"
import type { ShipmentData } from "@/components/ShipmentForm"
import { supabase } from "@/lib/supabase"

interface RankRequest extends ShipmentData {
  analysisDepth?: number
}

export async function POST(request: NextRequest) {
  try {
    const data: RankRequest = await request.json()

    // Default analysis depth if not provided
    const analysisDepth = data.analysisDepth || 3

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

    // Fetch forwarders from Supabase
    const { data: forwarders, error: forwardersError } = await supabase.from("forwarders").select("*")

    if (forwardersError) {
      console.error("Error fetching forwarders:", forwardersError)
      return NextResponse.json({ error: "Failed to fetch forwarders" }, { status: 500 })
    }

    // Fetch route information
    const { data: routes, error: routesError } = await supabase
      .from("routes")
      .select("*")
      .eq("origin_country", data.origin)
      .eq("destination_country", data.destination)
      .single()

    if (routesError && routesError.code !== "PGRST116") {
      // PGRST116 is "no rows returned"
      console.error("Error fetching route:", routesError)
      return NextResponse.json({ error: "Failed to fetch route information" }, { status: 500 })
    }

    const routeId = routes?.id

    // If we have a route, fetch rate cards
    let rateCards = []
    if (routeId) {
      const { data: cards, error: cardsError } = await supabase
        .from("rate_cards")
        .select("*, forwarder:forwarders(*)")
        .eq("route_id", routeId)
        .eq("cargo_type", data.cargoType)

      if (cardsError) {
        console.error("Error fetching rate cards:", cardsError)
      } else {
        rateCards = cards || []
      }
    }

    // If we have rate cards, use them to generate results
    // Otherwise, fall back to mock data
    let results = []

    if (rateCards.length > 0) {
      results = rateCards.map((card: any) => {
        const forwarder = card.forwarder

        // Calculate normalized factors (0-1 scale, lower is better for cost and time)
        const costFactor = (card.base_cost - 500) / 1500 // Normalize to 0-1 range
        const timeFactor = (routes?.typical_transit_days || 15) / 30 // Normalize to 0-1 range

        // Get forwarder services to determine if they have tracking
        const hasTracking = card.forwarder_services?.has_tracking || Math.random() > 0.3

        // For reliability, we'd ideally get this from performance_analytics
        // For now, generate a random value between 0.7 and 0.95
        const reliabilityFactor = 0.7 + Math.random() * 0.25

        // Calculate TOPSIS score
        const score =
          weights.cost * (1 - costFactor) +
          weights.time * (1 - timeFactor) +
          weights.reliability * reliabilityFactor +
          weights.tracking * (hasTracking ? 1 : 0)

        return {
          id: forwarder.id,
          name: forwarder.name,
          score,
          cost: Math.round(card.base_cost * (1 + (data.weight / 1000) * (card.cost_per_kg || 0.1))),
          deliveryTime: routes?.typical_transit_days || Math.round(10 + Math.random() * 10),
          reliability: Math.round(reliabilityFactor * 100),
          hasTracking,
          costFactor,
          timeFactor,
          reliabilityFactor,
        }
      })
    } else {
      // Fall back to mock data
      results = generateMockResults(data, weights, analysisDepth)
    }

    // Sort by score (descending)
    results.sort((a: any, b: any) => b.score - a.score)

    // Assign ranks
    results.forEach((result: any, index: number) => {
      result.rank = index + 1
    })

    // Add advanced analysis data if requested
    if (analysisDepth >= 4) {
      results = results.map((result: any) => {
        result.criterionContributions = [
          (weights.cost * (1 - result.costFactor)) / result.score,
          (weights.time * (1 - result.timeFactor)) / result.score,
          (weights.reliability * result.reliabilityFactor) / result.score,
          (weights.tracking * (result.hasTracking ? 1 : 0)) / result.score,
        ]

        result.commentary = generateForwarderCommentary(result, data)
        return result
      })
    }

    // Add sensitivity analysis if requested
    if (analysisDepth >= 5) {
      results = results.map((result: any) => {
        result.sensitivityAnalysis = {
          weightChanges: [
            "Cost: +10%",
            "Cost: -10%",
            "Time: +10%",
            "Time: -10%",
            "Reliability: +10%",
            "Reliability: -10%",
          ],
          scoreChanges: [
            calculateScoreChange(result, { ...weights, cost: weights.cost * 1.1 }),
            calculateScoreChange(result, { ...weights, cost: weights.cost * 0.9 }),
            calculateScoreChange(result, { ...weights, time: weights.time * 1.1 }),
            calculateScoreChange(result, { ...weights, time: weights.time * 0.9 }),
            calculateScoreChange(result, { ...weights, reliability: weights.reliability * 1.1 }),
            calculateScoreChange(result, { ...weights, reliability: weights.reliability * 0.9 }),
          ],
        }
        return result
      })
    }

    // Generate commentary
    const commentary = generateCommentary(results, data)

    // Save analysis to Supabase if user is authenticated
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (user) {
        await supabase.from("user_analyses").insert({
          user_id: user.id,
          analysis_name: `${data.origin} to ${data.destination}`,
          forwarders: results,
          results: {
            topForwarder: results[0]?.name,
            score: results[0]?.score,
            weights,
          },
          parameters: data,
        })
      }
    } catch (saveError) {
      console.error("Error saving analysis:", saveError)
      // Continue even if saving fails
    }

    return NextResponse.json({
      results,
      weights,
      commentary,
      analysisDepth,
    })
  } catch (error) {
    console.error("Error processing rank request:", error)
    return NextResponse.json({ error: "Failed to process ranking request" }, { status: 500 })
  }
}

// Mock function to generate results - would be replaced by actual backend call
function generateMockResults(data: RankRequest, weights: any, analysisDepth: number) {
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

  return results
}

// Helper function to calculate score change percentage
function calculateScoreChange(result: any, newWeights: any) {
  const originalScore = result.score

  // Calculate new score with adjusted weights
  const newScore =
    newWeights.cost * (1 - result.costFactor) +
    newWeights.time * (1 - result.timeFactor) +
    newWeights.reliability * result.reliabilityFactor +
    newWeights.tracking * (result.hasTracking ? 1 : 0)

  // Return percentage change
  return ((newScore - originalScore) / originalScore) * 100
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

