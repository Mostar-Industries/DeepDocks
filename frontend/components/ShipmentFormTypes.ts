export interface ShipmentData {
  origin: string
  destination: string
  weight: number
  volume?: number
  value?: number
  cargoType: string
  itemCategory?: string
  emergencyGrade?: string
  fragile: boolean
  hazardous: boolean
  perishable: boolean
  urgency: "standard" | "express" | "rush"
  carrier?: string
  shipmentMode?: string
}

