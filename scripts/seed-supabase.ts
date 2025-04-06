/**
 * DeepCAL++ Supabase Seeding Script
 * This script seeds the Supabase database with sample data
 */
import { createClient } from "@supabase/supabase-js"
import fs from "fs"
import path from "path"

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ""
const supabaseKey = process.env.SUPABASE_SERVICE_KEY || ""

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey)

async function seedDatabase() {
  console.log("Starting database seeding...")

  try {
    // Load forwarders data
    const forwardersPath = path.join(process.cwd(), "backend", "data", "forwarders.json")
    const forwardersData = JSON.parse(fs.readFileSync(forwardersPath, "utf8"))

    // Insert forwarders
    console.log(`Inserting ${forwardersData.length} forwarders...`)
    for (const forwarder of forwardersData) {
      const { routes, ...forwarderData } = forwarder

      // Insert forwarder
      const { data: insertedForwarder, error: forwarderError } = await supabase
        .from("forwarders")
        .upsert({
          id: forwarder.id,
          name: forwarder.name,
          code: forwarder.id.toUpperCase(),
          description: forwarder.description,
          country: forwarder.country,
          region: forwarder.region,
        })
        .select()
        .single()

      if (forwarderError) {
        console.error(`Error inserting forwarder ${forwarder.name}:`, forwarderError)
        continue
      }

      console.log(`Inserted forwarder: ${forwarder.name}`)

      // Insert routes and rate cards
      if (routes && routes.length > 0) {
        for (const route of routes) {
          // Check if route exists
          const { data: existingRoutes, error: routeQueryError } = await supabase
            .from("routes")
            .select("id")
            .eq("origin_country", route.origin)
            .eq("destination_country", route.destination)

          if (routeQueryError) {
            console.error(`Error querying route ${route.origin} to ${route.destination}:`, routeQueryError)
            continue
          }

          let routeId: string

          // Insert route if it doesn't exist
          if (!existingRoutes || existingRoutes.length === 0) {
            const { data: insertedRoute, error: routeError } = await supabase
              .from("routes")
              .insert({
                origin_country: route.origin,
                destination_country: route.destination,
                typical_transit_days: route.time,
              })
              .select()
              .single()

            if (routeError) {
              console.error(`Error inserting route ${route.origin} to ${route.destination}:`, routeError)
              continue
            }

            routeId = insertedRoute.id
            console.log(`Inserted route: ${route.origin} to ${route.destination}`)
          } else {
            routeId = existingRoutes[0].id
          }

          // Insert rate card
          const { error: rateCardError } = await supabase.from("rate_cards").upsert({
            forwarder_id: forwarder.id,
            route_id: routeId,
            cargo_type: "general",
            base_cost: route.cost,
            cost_per_kg: route.cost / 1000, // Approximate cost per kg
            effective_date: new Date().toISOString().split("T")[0],
          })

          if (rateCardError) {
            console.error(
              `Error inserting rate card for ${forwarder.name} on route ${route.origin} to ${route.destination}:`,
              rateCardError,
            )
            continue
          }

          console.log(`Inserted rate card for ${forwarder.name} on route ${route.origin} to ${route.destination}`)
        }
      }
    }

    console.log("Database seeding completed successfully!")
  } catch (error) {
    console.error("Error seeding database:", error)
  }
}

// Run the seeding function
seedDatabase()

