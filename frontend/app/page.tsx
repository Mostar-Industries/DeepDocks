"use client"

import Link from "next/link"
import { useState } from "react"
import CosmicShipmentForm from "@/components/CosmicShipmentForm"
import CosmicAnalysisDashboard from "@/components/CosmicAnalysisDashboard"
import type { ShipmentData } from "@/components/ShipmentForm"
import FuturisticHeader from "@/components/FuturisticHeader"

export default function Home() {
  const [shipmentData, setShipmentData] = useState<ShipmentData | null>(null)

  const handleSubmit = (data: ShipmentData) => {
    setShipmentData(data)
  }

  const handleReset = () => {
    setShipmentData(null)
  }

  return (
    <main className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="container mx-auto">
        <div className="flex justify-between items-center mb-8">
          <FuturisticHeader
            title="DeepCAL++ Logistics Portal"
            subtitle="Advanced logistics recommendation system with voice interaction"
          />

          <Link
            href="/dashboard"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Dashboard
          </Link>
        </div>

        <div className="max-w-4xl mx-auto">
          {shipmentData ? (
            <CosmicAnalysisDashboard shipmentData={shipmentData} onReset={handleReset} />
          ) : (
            <CosmicShipmentForm onSubmit={handleSubmit} />
          )}
        </div>
      </div>
    </main>
  )
}

