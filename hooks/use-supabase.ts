"use client"

import { useState } from "react"
import { supabase } from "@/lib/supabase"
import type { Forwarder, Route, RateCard, UserAnalysis } from "@/lib/supabase"

export function useSupabase() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch all forwarders
  const getForwarders = async (): Promise<Forwarder[]> => {
    setIsLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase.from("forwarders").select("*").order("name")

      if (error) throw error

      return data || []
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      console.error("Error fetching forwarders:", err)
      return []
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch routes
  const getRoutes = async (): Promise<Route[]> => {
    setIsLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase.from("routes").select("*")

      if (error) throw error

      return data || []
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      console.error("Error fetching routes:", err)
      return []
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch rate cards for a specific route and cargo type
  const getRateCards = async (routeId: string, cargoType: string): Promise<RateCard[]> => {
    setIsLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase
        .from("rate_cards")
        .select("*, forwarders(*)")
        .eq("route_id", routeId)
        .eq("cargo_type", cargoType)
        .lte("effective_date", new Date().toISOString())
        .or(`expiration_date.gt.${new Date().toISOString()},expiration_date.is.null`)

      if (error) throw error

      return data || []
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      console.error("Error fetching rate cards:", err)
      return []
    } finally {
      setIsLoading(false)
    }
  }

  // Save analysis results
  const saveAnalysis = async (
    analysisName: string,
    forwarders: any,
    results: any,
    parameters?: any,
  ): Promise<UserAnalysis | null> => {
    setIsLoading(true)
    setError(null)

    try {
      // Get the current user
      const {
        data: { user },
      } = await supabase.auth.getUser()

      const { data, error } = await supabase
        .from("user_analyses")
        .insert({
          user_id: user?.id,
          analysis_name: analysisName,
          forwarders,
          results,
          parameters,
        })
        .select()
        .single()

      if (error) throw error

      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      console.error("Error saving analysis:", err)
      return null
    } finally {
      setIsLoading(false)
    }
  }

  // Get user's saved analyses
  const getUserAnalyses = async (): Promise<UserAnalysis[]> => {
    setIsLoading(true)
    setError(null)

    try {
      // Get the current user
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) {
        return []
      }

      const { data, error } = await supabase
        .from("user_analyses")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })

      if (error) throw error

      return data || []
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      console.error("Error fetching user analyses:", err)
      return []
    } finally {
      setIsLoading(false)
    }
  }

  return {
    getForwarders,
    getRoutes,
    getRateCards,
    saveAnalysis,
    getUserAnalyses,
    isLoading,
    error,
  }
}

