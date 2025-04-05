import { type NextRequest, NextResponse } from "next/server"
import { generateSpeech } from "@/backend/voice/nigerian_voice_service"

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json()

    if (!text) {
      return NextResponse.json({ error: "Text is required" }, { status: 400 })
    }

    // Generate speech with Nigerian male voice
    const audioBuffer = await generateSpeech(text)

    if (!audioBuffer) {
      // If the server TTS fails, return an error so the client can fallback to browser TTS
      return NextResponse.json({ error: "Failed to generate speech" }, { status: 500 })
    }

    // Return audio data
    return new Response(audioBuffer, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "public, max-age=86400", // Cache for 24 hours
      },
    })
  } catch (error) {
    console.error("Error generating speech:", error)
    return NextResponse.json(
      {
        error: "Failed to generate speech",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}

