import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabaseUrl = Deno.env.get("SUPABASE_URL") || ""
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || ""
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Fetch data from Supabase
    const [
      { data: forwarders, error: forwardersError },
      { data: routes, error: routesError },
      { data: rateCards, error: rateCardsError },
      { data: forwarderServices, error: servicesError },
      { data: performanceAnalytics, error: analyticsError },
      { data: shipments, error: shipmentsError },
    ] = await Promise.all([
      supabase.from("forwarders").select("*"),
      supabase.from("routes").select("*"),
      supabase.from("rate_cards").select("*"),
      supabase.from("forwarder_services").select("*"),
      supabase.from("performance_analytics").select("*"),
      supabase.from("shipments").select("*"),
    ])

    // Check for errors
    if (forwardersError || routesError || rateCardsError || servicesError || analyticsError || shipmentsError) {
      throw new Error("Error fetching data from Supabase")
    }

    // Combine all data
    const supabaseData = {
      forwarders,
      routes,
      rate_cards: rateCards,
      forwarder_services: forwarderServices,
      performance_analytics: performanceAnalytics,
      shipments,
    }

    // Call the DeepCAL++ API to mirror data
    const apiUrl = Deno.env.get("DEEPCAL_API_URL") || "http://localhost:3000/api/mirror-data"
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${Deno.env.get("DEEPCAL_API_KEY") || ""}`,
      },
      body: JSON.stringify(supabaseData),
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const result = await response.json()

    return new Response(
      JSON.stringify({
        success: true,
        message: "Data mirrored successfully",
        timestamp: new Date().toISOString(),
        result,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString(),
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 500,
      },
    )
  }
})

