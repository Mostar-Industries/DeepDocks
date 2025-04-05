"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"

export default function AnalysisPage() {
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitted(true)
  }

  return (
    <main className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-6">
          <Link href="/" className="text-blue-400 hover:text-blue-300 flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-white mb-6">Logistics Analysis</h1>

        {!isSubmitted ? (
          <div className="bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6 text-white">
            <h2 className="text-xl font-bold text-blue-400 mb-4">Shipment Details</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Origin</label>
                  <select
                    className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white"
                    required
                  >
                    <option value="">Select origin</option>
                    <option value="Kenya">Kenya</option>
                    <option value="Nigeria">Nigeria</option>
                    <option value="South Africa">South Africa</option>
                    <option value="Ghana">Ghana</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Destination</label>
                  <select
                    className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white"
                    required
                  >
                    <option value="">Select destination</option>
                    <option value="DR Congo">DR Congo</option>
                    <option value="Egypt">Egypt</option>
                    <option value="Ethiopia">Ethiopia</option>
                    <option value="Morocco">Morocco</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Weight (kg)</label>
                  <input
                    type="number"
                    className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white"
                    placeholder="Enter weight"
                    min="1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Value (USD)</label>
                  <input
                    type="number"
                    className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white"
                    placeholder="Enter value"
                    min="1"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Cargo Type</label>
                <select className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white" required>
                  <option value="">Select cargo type</option>
                  <option value="general">General Merchandise</option>
                  <option value="electronics">Electronics</option>
                  <option value="perishable">Perishable Goods</option>
                  <option value="hazardous">Hazardous Materials</option>
                </select>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md"
                >
                  Analyze Logistics Options
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6 text-white">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-blue-400">Analysis Results</h2>
              <button onClick={() => setIsSubmitted(false)} className="text-sm text-gray-400 hover:text-white">
                New Analysis
              </button>
            </div>

            <div className="bg-blue-950/30 border border-blue-500/30 rounded-lg p-4 mb-6">
              <h3 className="font-medium text-blue-400 mb-2">Recommendation Summary</h3>
              <p>
                Based on your shipment details, we recommend <strong>ExpressShip</strong> as the optimal logistics
                forwarder with a score of <strong>0.723</strong>.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { name: "ExpressShip", score: 0.723, cost: "$1,450", time: "10 days", reliability: "92%" },
                { name: "AfricaLogistics", score: 0.651, cost: "$1,200", time: "14 days", reliability: "85%" },
                { name: "GlobalFreight", score: 0.487, cost: "$950", time: "18 days", reliability: "78%" },
              ].map((forwarder, index) => (
                <div
                  key={index}
                  className={`rounded-lg p-4 ${
                    index === 0 ? "bg-green-950/30 border border-green-500/30" : "bg-gray-800/50 border border-gray-700"
                  }`}
                >
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium">{forwarder.name}</h4>
                    <span className={`text-sm ${index === 0 ? "text-green-400" : "text-gray-400"}`}>
                      {forwarder.score.toFixed(3)}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Cost:</span>
                      <span>{forwarder.cost}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Time:</span>
                      <span>{forwarder.time}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Reliability:</span>
                      <span>{forwarder.reliability}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

