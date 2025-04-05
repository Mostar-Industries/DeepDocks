export default function DemoPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 p-8">
      <div className="max-w-md w-full bg-black/40 backdrop-blur-sm border border-blue-500/30 rounded-xl p-8 text-white">
        <h1 className="text-2xl font-bold text-red-400 mb-4">Demo Removed</h1>
        <p className="mb-4">The demo page has been removed from this application. Please return to the main page.</p>
        <a href="/" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md">
          Return to Home
        </a>
      </div>
    </div>
  )
}

