// Base data from foundational_data.json
// This would normally be fetched from an API, but for this example we'll include it directly

export const baseData = {
  // Origin and destination countries from the data
  locations: ["Kenya", "DR Congo", "Ghana", "Nigeria", "South Africa", "Morocco", "Ethiopia", "Egypt"],

  // Item categories from the data
  itemCategories: [
    {
      id: "PPE",
      name: "Personal Protective Equipment",
      description: "Safety equipment including masks, gloves, and protective clothing",
    },
    { id: "MED", name: "Medical Supplies", description: "General medical supplies and equipment" },
    { id: "PHARMA", name: "Pharmaceuticals", description: "Medicines and pharmaceutical products" },
    { id: "LAB", name: "Laboratory Supplies", description: "Equipment and supplies for laboratory use" },
    { id: "FOOD", name: "Food and Nutrition", description: "Food supplies and nutritional products" },
    {
      id: "WASH",
      name: "Water, Sanitation, and Hygiene",
      description: "Supplies related to water, sanitation, and hygiene",
    },
    { id: "TECH", name: "Technology Equipment", description: "Computers, communication devices, and other technology" },
    {
      id: "INFRA",
      name: "Infrastructure Materials",
      description: "Materials for building and infrastructure development",
    },
  ],

  // Emergency grades from the data
  emergencyGrades: [
    { id: "G1", name: "Grade 1", description: "Highest emergency priority, requires immediate action" },
    { id: "G2", name: "Grade 2", description: "High emergency priority, requires expedited processing" },
    { id: "G3", name: "Grade 3", description: "Moderate emergency priority, requires timely processing" },
    { id: "G4", name: "Grade 4", description: "Low emergency priority, standard processing acceptable" },
    { id: "G5", name: "Grade 5", description: "No emergency priority, routine processing" },
  ],

  // Carriers from the data
  carriers: [
    { id: "KN", name: "Kuehne Nagel", description: "Global logistics provider with extensive network" },
    {
      id: "SGL",
      name: "Scan Global Logistics",
      description: "International freight forwarder specializing in complex logistics",
    },
    {
      id: "DHLE",
      name: "DHL Express",
      description: "Express delivery service with time-definite international shipments",
    },
    { id: "DHLG", name: "DHL Global", description: "Global freight forwarding and supply chain solutions" },
    { id: "BWS", name: "Bwosi", description: "Regional logistics provider in Africa" },
    { id: "AGL", name: "AGL", description: "Africa-focused logistics and freight forwarding company" },
    { id: "SGN", name: "Siginon", description: "East African logistics provider" },
    { id: "FIT", name: "Freight in Time", description: "Specialized logistics provider for time-sensitive shipments" },
  ],

  // Shipment modes from the data
  shipmentModes: [
    { id: "AIR", name: "Air", description: "Shipment transported by aircraft" },
    { id: "SEA", name: "Sea", description: "Shipment transported by sea vessel" },
    { id: "ROA", name: "Road", description: "Shipment transported by road vehicle" },
    { id: "RAI", name: "Rail", description: "Shipment transported by rail" },
    { id: "MUL", name: "Multimodal", description: "Shipment using multiple transportation modes" },
  ],

  // Example shipment data from the data
  exampleShipments: [
    {
      origin: "Kenya",
      destination: "DR Congo",
      weight_kg: 192.7,
      volume_cbm: 0.94,
      item_category: "PPE",
      emergency_grade: "Grade 3",
      carrier: "Kuehne Nagel",
      mode_of_shipment: "Air",
    },
    {
      origin: "Ghana",
      destination: "Nigeria",
      weight_kg: 350.5,
      volume_cbm: 1.75,
      item_category: "MED",
      emergency_grade: "Grade 2",
      carrier: "DHL Express",
      mode_of_shipment: "Air",
    },
  ],
}

// Helper function to get a random item from an array
export function getRandomItem<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]
}

// Get a random example shipment
export function getRandomShipment() {
  return getRandomItem(baseData.exampleShipments)
}

// Map emergency grade to urgency
export function mapEmergencyGradeToUrgency(grade: string): "standard" | "express" | "rush" {
  switch (grade) {
    case "Grade 1":
      return "rush"
    case "Grade 2":
      return "express"
    case "Grade 3":
      return "express"
    case "Grade 4":
      return "standard"
    case "Grade 5":
      return "standard"
    default:
      return "standard"
  }
}

// Map item category to cargo type
export function mapItemCategoryToCargoType(category: string): string {
  const categoryMap: { [key: string]: string } = {
    PPE: "ppe",
    MED: "medical",
    PHARMA: "pharmaceuticals",
    LAB: "laboratory",
    FOOD: "food",
    WASH: "wash",
    TECH: "technology",
    INFRA: "infrastructure",
  }

  return categoryMap[category] || "general"
}

