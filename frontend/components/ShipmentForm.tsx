"use client"

import type React from "react"
import { useState } from "react"

interface ShipmentFormProps {
  onSubmit: (data: ShipmentData) => void
}

export interface ShipmentData {
  origin: string
  destination: string
  weight: number
  value: number
  cargoType: string
  fragile: boolean
  hazardous: boolean
  perishable: boolean
  urgency: "standard" | "express" | "rush"
}

export const ShipmentForm: React.FC<ShipmentFormProps> = ({ onSubmit = () => {} }) => {
  // Initialize with complete default values
  const [formData, setFormData] = useState<ShipmentData>({
    origin: "Lagos, Nigeria",
    destination: "Cairo, Egypt",
    weight: 1000,
    value: 10000,
    cargoType: "general",
    fragile: false,
    hazardous: false,
    perishable: false,
    urgency: "standard",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = type === "checkbox" ? (e.target as HTMLInputElement).checked : undefined

    // Ensure numeric values are properly handled
    if (type === "number") {
      const numValue = Number.parseFloat(value)
      setFormData((prev) => ({
        ...prev,
        [name]: isNaN(numValue) ? 0 : numValue,
      }))
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: type === "checkbox" ? checked : value,
      }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Validate data before submission
    if (!formData.origin || !formData.destination) {
      alert("Please fill in all required fields")
      return
    }
    onSubmit(formData)
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Shipment Details</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Origin</label>
            <input
              type="text"
              name="origin"
              value={formData.origin}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="City, Country"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Destination</label>
            <input
              type="text"
              name="destination"
              value={formData.destination}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="City, Country"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Weight (kg)</label>
            <input
              type="number"
              name="weight"
              value={formData.weight}
              onChange={handleChange}
              min="0"
              step="0.01"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Declared Value (USD)</label>
            <input
              type="number"
              name="value"
              value={formData.value}
              onChange={handleChange}
              min="0"
              step="0.01"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Cargo Type</label>
          <select
            name="cargoType"
            value={formData.cargoType}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          >
            <option value="general">General Merchandise</option>
            <option value="electronics">Electronics</option>
            <option value="furniture">Furniture</option>
            <option value="vehicles">Vehicles</option>
            <option value="machinery">Machinery</option>
            <option value="textiles">Textiles</option>
            <option value="chemicals">Chemicals</option>
            <option value="food">Food Products</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              name="fragile"
              checked={formData.fragile}
              onChange={handleChange}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label className="ml-2 block text-sm text-gray-700">Fragile</label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="hazardous"
              checked={formData.hazardous}
              onChange={handleChange}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label className="ml-2 block text-sm text-gray-700">Hazardous</label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="perishable"
              checked={formData.perishable}
              onChange={handleChange}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label className="ml-2 block text-sm text-gray-700">Perishable</label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Urgency</label>
          <div className="mt-2 space-x-4">
            <div className="inline-flex items-center">
              <input
                type="radio"
                name="urgency"
                value="standard"
                checked={formData.urgency === "standard"}
                onChange={handleChange}
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label className="ml-2 block text-sm text-gray-700">Standard</label>
            </div>

            <div className="inline-flex items-center">
              <input
                type="radio"
                name="urgency"
                value="express"
                checked={formData.urgency === "express"}
                onChange={handleChange}
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label className="ml-2 block text-sm text-gray-700">Express</label>
            </div>

            <div className="inline-flex items-center">
              <input
                type="radio"
                name="urgency"
                value="rush"
                checked={formData.urgency === "rush"}
                onChange={handleChange}
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label className="ml-2 block text-sm text-gray-700">Rush</label>
            </div>
          </div>
        </div>

        <div className="pt-4">
          <button
            type="submit"
            className="w-full bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Calculate Logistics Options
          </button>
        </div>
      </form>
    </div>
  )
}

export default ShipmentForm

