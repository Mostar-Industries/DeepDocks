"use client"

import { useState, useEffect, useCallback } from "react"

// Types for anomalies
export interface Anomaly {
  id: string
  message: string
  level: "info" | "warning" | "critical"
  timestamp: Date
  source: string
  details?: any
}

type AnomalyHandler = (anomaly: Anomaly) => void

// This hook provides anomaly detection functionality
export function useAnomalyDetection() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [handlers, setHandlers] = useState<AnomalyHandler[]>([])

  // Register a handler for anomalies
  const registerAnomalyHandler = useCallback((handler: AnomalyHandler) => {
    setHandlers((prev) => [...prev, handler])

    // Return unregister function
    return () => {
      setHandlers((prev) => prev.filter((h) => h !== handler))
    }
  }, [])

  // Function to add an anomaly
  const addAnomaly = useCallback(
    (anomaly: Anomaly) => {
      setAnomalies((prev) => [...prev, anomaly])

      // Call all handlers
      handlers.forEach((handler) => handler(anomaly))
    },
    [handlers],
  )

  // Function to clear anomalies
  const clearAnomalies = useCallback(() => {
    setAnomalies([])
  }, [])

  // Set up WebSocket connection for real-time anomaly detection
  useEffect(() => {
    // In a real implementation, this would connect to your backend
    // For now, we'll simulate anomalies

    const simulateAnomalies = () => {
      // Simulate random anomalies for demonstration
      const randomAnomaly = () => {
        const levels = ["info", "warning", "critical"] as const
        const level = levels[Math.floor(Math.random() * levels.length)]

        const messages = {
          info: [
            "Shipment data updated for route KEN-DRC",
            "New logistics provider available for East Africa region",
            "System performance metrics updated",
          ],
          warning: [
            "Potential delay detected in Nigeria-Ghana route",
            "Weather conditions may affect delivery times in East Africa",
            "Data completeness below threshold for South Africa shipments",
          ],
          critical: [
            "Critical delay detected in Kenya-DRC route",
            "System unable to connect to logistics provider API",
            "Data integrity issue detected in shipment records",
          ],
        }

        const message = messages[level][Math.floor(Math.random() * messages[level].length)]

        return {
          id: `anomaly-${Date.now()}`,
          message,
          level,
          timestamp: new Date(),
          source: "DeepCAL++ Analytics",
        }
      }

      // Add a random anomaly every 30-60 seconds
      const interval = setInterval(() => {
        // 20% chance of generating an anomaly
        if (Math.random() < 0.2) {
          const anomaly = randomAnomaly()
          addAnomaly(anomaly)
        }
      }, 30000)

      // Generate one anomaly immediately for demonstration
      setTimeout(() => {
        const anomaly: Anomaly = {
          id: `anomaly-${Date.now()}`,
          message: "Data completeness below threshold for Nigeria-Ghana route",
          level: "warning",
          timestamp: new Date(),
          source: "DeepCAL++ Analytics",
        }

        addAnomaly(anomaly)
      }, 5000)

      return () => clearInterval(interval)
    }

    const cleanup = simulateAnomalies()

    return () => {
      cleanup()
    }
  }, [addAnomaly])

  return {
    anomalies,
    addAnomaly,
    clearAnomalies,
    registerAnomalyHandler,
  }
}

