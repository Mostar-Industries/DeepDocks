"use client"

import type React from "react"

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
}

interface ResultCardProps {
  result: ForwarderResult
  isRecommended: boolean
  onSelect: (forwarderId: string) => void
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, isRecommended = false, onSelect = () => {} }) => {
  // Check if result is undefined or null
  if (!result) {
    return (
      <div className="border rounded-lg overflow-hidden shadow-md bg-gray-100 p-6 text-center">
        <h3 className="font-medium text-gray-500">Forwarder Data Unavailable</h3>
        <p className="text-sm text-gray-400 mt-2">The requested forwarder information could not be loaded.</p>
      </div>
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
  } = result

  // Calculate factor bars (values between 0-100 for display)
  const costBar = 100 - costFactor * 100 // Inverse for cost (lower is better)
  const timeBar = 100 - timeFactor * 100 // Inverse for time (lower is better)
  const reliabilityBar = reliabilityFactor * 100

  return (
    <div
      className={`border rounded-lg overflow-hidden shadow-md transition-all duration-200 ${
        isRecommended ? "border-green-500 bg-green-50" : "border-gray-200 bg-white hover:shadow-lg"
      }`}
    >
      {/* Header */}
      <div className={`px-4 py-3 ${isRecommended ? "bg-green-500 text-white" : "bg-gray-100"}`}>
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-lg">{name}</h3>
          {isRecommended && (
            <span className="bg-white text-green-600 text-xs font-semibold px-2 py-1 rounded-full">RECOMMENDED</span>
          )}
        </div>
        <div className="text-sm mt-1">
          Rank: {rank} • Score: {score.toFixed(3)}
        </div>
      </div>

      {/* Body */}
      <div className="p-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <span className="text-gray-600 text-sm">Cost</span>
            <div className="text-xl font-semibold">${cost.toLocaleString()}</div>
          </div>
          <div>
            <span className="text-gray-600 text-sm">Delivery Time</span>
            <div className="text-xl font-semibold">{deliveryTime} days</div>
          </div>
        </div>

        {/* Factors Visualization */}
        <div className="space-y-3 my-4">
          <div>
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Cost Efficiency</span>
              <span>{costBar.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${costBar}%` }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Time Efficiency</span>
              <span>{timeBar.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${timeBar}%` }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Reliability</span>
              <span>{reliabilityBar.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${reliabilityBar}%` }}></div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="flex items-center mt-4 text-sm">
          <div className="mr-4">
            <span className={`inline-flex items-center ${hasTracking ? "text-green-600" : "text-gray-400"}`}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Tracking
            </span>
          </div>
          <div>
            <span className="inline-flex items-center text-gray-600">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {deliveryTime} days
            </span>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={() => onSelect(id)}
          className={`w-full mt-4 py-2 px-4 rounded-md text-sm font-medium 
            ${
              isRecommended
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
        >
          {isRecommended ? "Select Recommended" : "Select This Option"}
        </button>
      </div>
    </div>
  )
}

export default ResultCard

