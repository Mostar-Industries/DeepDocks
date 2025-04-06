import { type NextRequest, NextResponse } from "next/server"
import { stop_speaking } from "@/backend/voice/speak"

export async function POST(request: NextRequest) {
  try {
    const success = stop_speaking()

    if (success) {
      return NextResponse.json({ success: true })
    } else {
      return NextResponse.json({ error: "Failed to stop speech" }, { status: 500 })
    }
  } catch (error) {
    console.error("Error stopping speech:", error)
    return NextResponse.json({ error: "Failed to stop speech" }, { status: 500 })
  }
}

