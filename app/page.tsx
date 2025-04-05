import Link from "next/link"

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-900 flex items-center justify-center p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-white mb-6">DeepCAL++ System</h1>

        <div className="bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-8 text-white">
          <h2 className="text-2xl font-bold text-blue-400 mb-4">African Logistics Forwarder Recommendation System</h2>
          <p className="mb-6">
            DeepCAL++ is an advanced decision support system for logistics optimization, featuring intelligent forwarder
            ranking and comprehensive analysis tools.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <div className="bg-blue-950/30 border border-blue-500/30 rounded-lg p-6">
              <h3 className="text-xl font-bold text-blue-400 mb-2">Logistics Analysis</h3>
              <p className="text-sm mb-4">
                Use our TOPSIS-based analysis to find the optimal logistics forwarder for your shipments.
              </p>
              <Link
                href="/analysis"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
              >
                Start Analysis
              </Link>
            </div>

            <div className="bg-purple-950/30 border border-purple-500/30 rounded-lg p-6">
              <h3 className="text-xl font-bold text-purple-400 mb-2">Documentation</h3>
              <p className="text-sm mb-4">Learn more about how DeepCAL++ can optimize your logistics operations.</p>
              <Link
                href="/docs"
                className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
              >
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

