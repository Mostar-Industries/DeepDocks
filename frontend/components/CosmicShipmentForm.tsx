"use client"

import type React from "react"

import { useState } from "react"
import { Package, Truck, MapPin, Weight, DollarSign, AlertTriangle, Zap, Rocket } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Define the ShipmentData interface
export interface ShipmentData {
  origin: string
  destination: string
  weight: number
  value?: number
  cargoType: string
  itemCategory?: string
  emergencyGrade?: string
  fragile: boolean
  hazardous: boolean
  perishable: boolean
  urgency: "standard" | "express" | "rush"
}

interface CosmicShipmentFormProps {
  onSubmit?: (data: ShipmentData) => void
}

// Base data from the actual system
const baseData = {
  locations: ["Kenya", "DR Congo", "Ghana", "Nigeria", "South Africa", "Morocco", "Ethiopia", "Egypt"],
  itemCategories: [
    { id: "PPE", name: "Personal Protective Equipment" },
    { id: "MED", name: "Medical Supplies" },
    { id: "PHARMA", name: "Pharmaceuticals" },
    { id: "LAB", name: "Laboratory Supplies" },
    { id: "FOOD", name: "Food and Nutrition" },
    { id: "WASH", name: "Water, Sanitation, and Hygiene" },
    { id: "TECH", name: "Technology Equipment" },
    { id: "INFRA", name: "Infrastructure Materials" },
  ],
  emergencyGrades: [
    { id: "G1", name: "Grade 1", description: "Highest emergency priority" },
    { id: "G2", name: "Grade 2", description: "High emergency priority" },
    { id: "G3", name: "Grade 3", description: "Moderate emergency priority" },
    { id: "G4", name: "Grade 4", description: "Low emergency priority" },
    { id: "G5", name: "Grade 5", description: "No emergency priority" },
  ],
}

export default function CosmicShipmentForm({ onSubmit }: CosmicShipmentFormProps) {
  // Initialize with data from the base data
  const [formData, setFormData] = useState<ShipmentData>({
    origin: "Kenya",
    destination: "DR Congo",
    weight: 192.7,
    value: 10000,
    cargoType: "ppe",
    itemCategory: "PPE",
    emergencyGrade: "Grade 3",
    fragile: true,
    hazardous: false,
    perishable: false,
    urgency: "express",
  })

  const [formStep, setFormStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submittedData, setSubmittedData] = useState<ShipmentData | null>(null)

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

  // Handle select changes
  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.origin || !formData.destination) {
      alert("Please fill in all required fields")
      return
    }

    setIsSubmitting(true)

    // Simulate loading
    setTimeout(() => {
      // Store the submitted data locally if no onSubmit handler
      setSubmittedData(formData)

      // Call the onSubmit handler if provided
      if (typeof onSubmit === "function") {
        onSubmit(formData)
      } else {
        console.log("Form submitted with data:", formData)
      }

      setIsSubmitting(false)
    }, 1000)
  }

  const nextStep = () => {
    setFormStep((prev) => Math.min(prev + 1, 2))
  }

  const prevStep = () => {
    setFormStep((prev) => Math.max(prev - 1, 0))
  }

  const getStepTitle = () => {
    switch (formStep) {
      case 0:
        return "Origin & Destination"
      case 1:
        return "Cargo Details"
      case 2:
        return "Shipment Priority"
      default:
        return "Shipment Details"
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl overflow-hidden shadow-lg border border-blue-500/30 bg-black/40 backdrop-blur-sm">
        <div className="p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 rounded-full bg-black/40 backdrop-blur-sm">
              {formStep === 0 ? (
                <MapPin className="h-8 w-8 text-blue-400" />
              ) : formStep === 1 ? (
                <Package className="h-8 w-8 text-pink-400" />
              ) : (
                <Rocket className="h-8 w-8 text-green-400" />
              )}
            </div>

            <div>
              <h2 className="text-2xl font-bold text-blue-400">{getStepTitle()}</h2>
              <p className="text-gray-400">Please provide the shipment details</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1: Origin and Destination */}
            {formStep === 0 && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-blue-400" />
                      <span>Origin Country</span>
                    </Label>
                    <Select value={formData.origin} onValueChange={(value) => handleSelectChange("origin", value)}>
                      <SelectTrigger className="bg-black/40 border-blue-500/30 focus:border-blue-500 h-12">
                        <SelectValue placeholder="Select origin country" />
                      </SelectTrigger>
                      <SelectContent className="bg-black/90 border-blue-500/30">
                        {baseData.locations.map((location) => (
                          <SelectItem key={location} value={location}>
                            {location}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-pink-400" />
                      <span>Destination Country</span>
                    </Label>
                    <Select
                      value={formData.destination}
                      onValueChange={(value) => handleSelectChange("destination", value)}
                    >
                      <SelectTrigger className="bg-black/40 border-pink-500/30 focus:border-pink-500 h-12">
                        <SelectValue placeholder="Select destination country" />
                      </SelectTrigger>
                      <SelectContent className="bg-black/90 border-pink-500/30">
                        {baseData.locations.map((location) => (
                          <SelectItem key={location} value={location}>
                            {location}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="mt-8 flex justify-end">
                  <Button type="button" onClick={nextStep} className="bg-blue-600 hover:bg-blue-700 text-white px-8">
                    <span>Next Step</span>
                    <Zap className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}

            {/* Step 2: Cargo Details */}
            {formStep === 1 && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Weight className="h-4 w-4 text-blue-400" />
                      <span>Cargo Weight (kg)</span>
                    </Label>
                    <div className="relative">
                      <Input
                        type="number"
                        name="weight"
                        value={formData.weight}
                        onChange={handleChange}
                        min="0"
                        step="0.01"
                        className="bg-black/40 border-blue-500/30 focus:border-blue-500 pl-10 h-12"
                        required
                      />
                      <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                        <Weight size={16} className="text-blue-400" />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-green-400" />
                      <span>Cargo Value (USD)</span>
                    </Label>
                    <div className="relative">
                      <Input
                        type="number"
                        name="value"
                        value={formData.value}
                        onChange={handleChange}
                        min="0"
                        step="0.01"
                        className="bg-black/40 border-green-500/30 focus:border-green-500 pl-10 h-12"
                      />
                      <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                        <DollarSign size={16} className="text-green-400" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-pink-400" />
                    <span>Item Category</span>
                  </Label>
                  <Select
                    value={formData.itemCategory}
                    onValueChange={(value) => handleSelectChange("itemCategory", value)}
                  >
                    <SelectTrigger className="bg-black/40 border-pink-500/30 focus:border-pink-500 h-12">
                      <SelectValue placeholder="Select item category" />
                    </SelectTrigger>
                    <SelectContent className="bg-black/90 border-pink-500/30">
                      {baseData.itemCategories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <Card className="bg-black/40 border-blue-500/30 p-4">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="fragile"
                        name="fragile"
                        checked={formData.fragile}
                        onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, fragile: checked === true }))}
                        className="border-blue-500/50 data-[state=checked]:bg-blue-500"
                      />
                      <Label htmlFor="fragile" className="text-sm">
                        <span>Fragile</span>
                      </Label>
                    </div>
                  </Card>

                  <Card className="bg-black/40 border-pink-500/30 p-4">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="hazardous"
                        name="hazardous"
                        checked={formData.hazardous}
                        onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, hazardous: checked === true }))}
                        className="border-pink-500/50 data-[state=checked]:bg-pink-500"
                      />
                      <Label htmlFor="hazardous" className="text-sm">
                        <span>Hazardous</span>
                      </Label>
                    </div>
                  </Card>

                  <Card className="bg-black/40 border-green-500/30 p-4">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="perishable"
                        name="perishable"
                        checked={formData.perishable}
                        onCheckedChange={(checked) =>
                          setFormData((prev) => ({ ...prev, perishable: checked === true }))
                        }
                        className="border-green-500/50 data-[state=checked]:bg-green-500"
                      />
                      <Label htmlFor="perishable" className="text-sm">
                        <span>Perishable</span>
                      </Label>
                    </div>
                  </Card>
                </div>

                <div className="mt-8 flex justify-between">
                  <Button
                    type="button"
                    onClick={prevStep}
                    variant="outline"
                    className="border-blue-500/30 text-blue-400 hover:bg-blue-950/30"
                  >
                    <span>Back</span>
                  </Button>

                  <Button type="button" onClick={nextStep} className="bg-pink-600 hover:bg-pink-700 text-white px-8">
                    <span>Next Step</span>
                    <Zap className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}

            {/* Step 3: Emergency Grade & Urgency */}
            {formStep === 2 && (
              <div className="space-y-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-pink-400" />
                      <span>Emergency Grade</span>
                    </Label>
                    <Select
                      value={formData.emergencyGrade}
                      onValueChange={(value) => handleSelectChange("emergencyGrade", value)}
                    >
                      <SelectTrigger className="bg-black/40 border-pink-500/30 focus:border-pink-500 h-12">
                        <SelectValue placeholder="Select emergency grade" />
                      </SelectTrigger>
                      <SelectContent className="bg-black/90 border-pink-500/30">
                        {baseData.emergencyGrades.map((grade) => (
                          <SelectItem key={grade.id} value={grade.name}>
                            {grade.name} - {grade.description}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-6 mt-6">
                    <div className="space-y-2">
                      <Label className="text-lg font-medium text-green-400">Shipment Priority</Label>
                      <p className="text-gray-400 text-sm">Select the priority level based on your emergency grade</p>
                    </div>

                    <RadioGroup
                      value={formData.urgency}
                      onValueChange={(value) =>
                        setFormData((prev) => ({ ...prev, urgency: value as "standard" | "express" | "rush" }))
                      }
                      className="grid grid-cols-1 md:grid-cols-3 gap-4"
                    >
                      <Label
                        htmlFor="standard"
                        className={`flex flex-col items-center justify-between rounded-lg border-2 p-4 cursor-pointer h-full
                          ${formData.urgency === "standard" ? "border-blue-500 bg-blue-950/20" : "border-gray-700"}`}
                      >
                        <RadioGroupItem value="standard" id="standard" className="sr-only" />
                        <Truck className="h-8 w-8 mb-3 text-blue-400" />
                        <div className="space-y-1 text-center">
                          <p className="font-medium">Standard</p>
                          <p className="text-xs text-gray-400">Grade 4-5</p>
                          <p className="text-xs text-gray-400">Regular shipping priority</p>
                        </div>
                      </Label>

                      <Label
                        htmlFor="express"
                        className={`flex flex-col items-center justify-between rounded-lg border-2 p-4 cursor-pointer h-full
                          ${formData.urgency === "express" ? "border-pink-500 bg-pink-950/20" : "border-gray-700"}`}
                      >
                        <RadioGroupItem value="express" id="express" className="sr-only" />
                        <Zap className="h-8 w-8 mb-3 text-pink-400" />
                        <div className="space-y-1 text-center">
                          <p className="font-medium">Express</p>
                          <p className="text-xs text-gray-400">Grade 2-3</p>
                          <p className="text-xs text-gray-400">Expedited processing</p>
                        </div>
                      </Label>

                      <Label
                        htmlFor="rush"
                        className={`flex flex-col items-center justify-between rounded-lg border-2 p-4 cursor-pointer h-full
                          ${formData.urgency === "rush" ? "border-green-500 bg-green-950/20" : "border-gray-700"}`}
                      >
                        <RadioGroupItem value="rush" id="rush" className="sr-only" />
                        <Rocket className="h-8 w-8 mb-3 text-green-400" />
                        <div className="space-y-1 text-center">
                          <p className="font-medium">Rush</p>
                          <p className="text-xs text-gray-400">Grade 1</p>
                          <p className="text-xs text-gray-400">Highest priority shipping</p>
                        </div>
                      </Label>
                    </RadioGroup>
                  </div>
                </div>

                <div className="mt-8 flex justify-between">
                  <Button
                    type="button"
                    onClick={prevStep}
                    variant="outline"
                    className="border-blue-500/30 text-blue-400 hover:bg-blue-950/30"
                  >
                    <span>Back</span>
                  </Button>

                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="bg-green-600 hover:bg-green-700 text-white px-8"
                  >
                    {isSubmitting ? "Processing..." : "Submit"}
                  </Button>
                </div>
              </div>
            )}
          </form>
        </div>
      </div>

      {/* Display submitted data if no onSubmit handler was provided */}
      {submittedData && !onSubmit && (
        <div className="p-6 bg-black/40 border border-green-500/30 rounded-xl">
          <h2 className="text-xl font-bold text-green-400 mb-4">Form Submitted Successfully!</h2>
          <pre className="bg-black/60 p-4 rounded overflow-auto text-gray-300">
            {JSON.stringify(submittedData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

