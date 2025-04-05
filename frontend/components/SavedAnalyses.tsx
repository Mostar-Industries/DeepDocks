"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useSupabase } from "@/hooks/use-supabase"
import { Clock, Calendar, ArrowRight } from "lucide-react"

export default function SavedAnalyses() {
  const { getUserAnalyses, isLoading, error } = useSupabase()
  const [analyses, setAnalyses] = useState<any[]>([])

  useEffect(() => {
    const fetchAnalyses = async () => {
      const data = await getUserAnalyses()
      setAnalyses(data)
    }

    fetchAnalyses()
  }, [getUserAnalyses])

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Saved Analyses</CardTitle>
          <CardDescription>Loading your previous analyses...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Saved Analyses</CardTitle>
          <CardDescription className="text-red-500">Error loading analyses: {error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (analyses.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Saved Analyses</CardTitle>
          <CardDescription>You don't have any saved analyses yet.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Saved Analyses</CardTitle>
        <CardDescription>View your previous logistics analyses</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {analyses.map((analysis) => (
            <Card key={analysis.id} className="bg-black/40 backdrop-blur-sm border-blue-500/30">
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-blue-400">{analysis.analysis_name || "Unnamed Analysis"}</h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(analysis.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{new Date(analysis.created_at).toLocaleTimeString()}</span>
                      </div>
                    </div>

                    {analysis.results && (
                      <div className="mt-2">
                        <p className="text-sm">
                          Top recommendation:{" "}
                          <span className="font-medium text-green-400">{analysis.results.topForwarder}</span>
                        </p>
                        <p className="text-xs text-gray-400">Score: {analysis.results.score?.toFixed(3)}</p>
                      </div>
                    )}
                  </div>

                  <Button size="sm" variant="outline" className="border-blue-500/30 text-blue-400">
                    <span>View</span>
                    <ArrowRight className="ml-2 h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

