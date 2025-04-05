import Link from "next/link"

export default function DocsPage() {
  return (
    <main className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-6">
          <Link href="/" className="text-blue-400 hover:text-blue-300 flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-white mb-6">DeepCAL++ Documentation</h1>

        <div className="bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6 text-white">
          <h2 className="text-xl font-bold text-blue-400 mb-4">System Overview</h2>

          <p className="mb-4">
            DeepCAL++ (Deep Contextual Assessment for Logistics) is an advanced decision support system for logistics
            optimization, featuring intelligent forwarder ranking and comprehensive analysis tools.
          </p>

          <h3 className="text-lg font-bold text-purple-400 mt-6 mb-2">Key Features</h3>

          <ul className="list-disc pl-6 space-y-2 mb-6">
            <li>TOPSIS-based multi-criteria decision making for optimal forwarder selection</li>
            <li>Comprehensive analysis of cost, time, reliability, and tracking factors</li>
            <li>African logistics specialization with regional expertise</li>
            <li>Data-driven recommendations based on historical performance</li>
            <li>Detailed visualization and reporting capabilities</li>
          </ul>

          <h3 className="text-lg font-bold text-purple-400 mt-6 mb-2">System Architecture</h3>

          <p className="mb-4">The system is organized into two main components:</p>

          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Backend:</strong> The brain of the system, containing all calculation, prediction, and voice
              processing logic
            </li>
            <li>
              <strong>Frontend:</strong> The face of the system, providing user interfaces and visualization
            </li>
          </ul>

          <div className="mt-8 p-4 bg-blue-950/30 border border-blue-500/30 rounded-lg">
            <h4 className="font-medium text-blue-400 mb-2">Getting Started</h4>
            <p className="mb-2">
              To begin using DeepCAL++, navigate to the Analysis page and enter your shipment details. The system will
              calculate the optimal logistics forwarder based on your specific requirements.
            </p>
            <Link
              href="/analysis"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md mt-2"
            >
              Start Analysis
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}

