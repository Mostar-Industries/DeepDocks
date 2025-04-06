import TestIntegration from "@/components/TestIntegration"

export default function TestPage() {
  return (
    <main className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold text-white mb-6">DeepCAL++ Integration Test</h1>
        <TestIntegration />
      </div>
    </main>
  )
}

