"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useSupabase } from "@/hooks/use-supabase"
import { Truck, MapPin, Globe, Phone, Mail } from "lucide-react"
import type { Forwarder } from "@/lib/supabase"

export default function ForwardersList() {
  const { getForwarders, isLoading, error } = useSupabase()
  const [forwarders, setForwarders] = useState<Forwarder[]>([])

  useEffect(() => {
    const fetchForwarders = async () => {
      const data = await getForwarders()
      setForwarders(data)
    }

    fetchForwarders()
  }, [getForwarders])

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Logistics Forwarders</CardTitle>
          <CardDescription>Loading forwarders...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Logistics Forwarders</CardTitle>
          <CardDescription className="text-red-500">Error loading forwarders: {error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (forwarders.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Logistics Forwarders</CardTitle>
          <CardDescription>No forwarders found in the database.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Logistics Forwarders</CardTitle>
        <CardDescription>Available logistics providers in our database</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {forwarders.map((forwarder) => (
            <Card key={forwarder.id} className="bg-black/40 backdrop-blur-sm border-blue-500/30">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-950/50 rounded-full">
                    <Truck className="h-5 w-5 text-blue-400" />
                  </div>

                  <div>
                    <h3 className="font-medium text-blue-400">{forwarder.name}</h3>

                    {forwarder.code && <p className="text-xs text-gray-400 mt-1">Code: {forwarder.code}</p>}

                    {forwarder.region && (
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                        <MapPin className="h-3 w-3" />
                        <span>{forwarder.region}</span>
                        {forwarder.country && <span>, {forwarder.country}</span>}
                      </div>
                    )}

                    {forwarder.website && (
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                        <Globe className="h-3 w-3" />
                        <a
                          href={forwarder.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-blue-400"
                        >
                          {forwarder.website.replace(/^https?:\/\//, "")}
                        </a>
                      </div>
                    )}

                    {forwarder.contact_phone && (
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                        <Phone className="h-3 w-3" />
                        <span>{forwarder.contact_phone}</span>
                      </div>
                    )}

                    {forwarder.contact_email && (
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                        <Mail className="h-3 w-3" />
                        <a href={`mailto:${forwarder.contact_email}`} className="hover:text-blue-400">
                          {forwarder.contact_email}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

