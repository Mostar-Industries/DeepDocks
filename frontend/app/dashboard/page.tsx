"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import FuturisticHeader from "@/components/FuturisticHeader"
import SavedAnalyses from "@/components/SavedAnalyses"
import ForwardersList from "@/components/ForwardersList"
import { Database, History, Truck } from "lucide-react"

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("analyses")

  return (
    <main className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="container mx-auto">
        <FuturisticHeader title="DeepCAL++ Dashboard" subtitle="View your saved analyses and logistics data" />

        <div className="max-w-6xl mx-auto mt-8">
          <Tabs defaultValue="analyses" value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="analyses" className="flex items-center gap-2">
                <History className="h-4 w-4" />
                <span>Saved Analyses</span>
              </TabsTrigger>
              <TabsTrigger value="forwarders" className="flex items-center gap-2">
                <Truck className="h-4 w-4" />
                <span>Forwarders</span>
              </TabsTrigger>
              <TabsTrigger value="data" className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                <span>Database</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="analyses">
              <SavedAnalyses />
            </TabsContent>

            <TabsContent value="forwarders">
              <ForwardersList />
            </TabsContent>

            <TabsContent value="data">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-2">
                  <div className="bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6">
                    <h2 className="text-xl font-bold text-blue-400 mb-4">Database Schema</h2>
                    <p className="text-gray-300 mb-4">
                      The DeepCAL++ system uses a Supabase PostgreSQL database with the following tables:
                    </p>

                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-medium text-blue-400">forwarders</h3>
                        <p className="text-sm text-gray-400">Stores information about logistics forwarders</p>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-blue-400">forwarder_services</h3>
                        <p className="text-sm text-gray-400">Services offered by each forwarder</p>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-blue-400">routes</h3>
                        <p className="text-sm text-gray-400">Shipping routes between origins and destinations</p>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-blue-400">rate_cards</h3>
                        <p className="text-sm text-gray-400">Pricing information for specific routes and cargo types</p>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-blue-400">shipments</h3>
                        <p className="text-sm text-gray-400">Historical shipment data</p>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium text-blue-400">user_analyses</h3>
                        <p className="text-sm text-gray-400">Saved analysis results from users</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </main>
  )
}

