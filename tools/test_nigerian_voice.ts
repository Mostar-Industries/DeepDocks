/**
 * Test script for the Nigerian voice service
 *
 * Usage:
 * ts-node tools/test_nigerian_voice.ts "Text to speak"
 */

import { generateSpeech, getVoiceStats } from "../backend/voice/nigerian_voice_service"
import fs from "fs"
import path from "path"
import { exec } from "child_process"
import { promisify } from "util"

const execAsync = promisify(exec)

async function main() {
  // Get the text to speak from command line arguments
  const text = process.argv[2] || "Hello, I am the Nigerian voice for DeepCAL++. How can I assist you today?"

  console.log(`Testing Nigerian voice with text: "${text}"`)

  try {
    // Get voice stats
    const stats = await getVoiceStats()
    console.log("Voice Service Stats:", stats)

    // Generate speech
    console.log("Generating speech...")
    const audioBuffer = await generateSpeech(text, true)

    if (!audioBuffer) {
      console.error("Failed to generate speech")
      process.exit(1)
    }

    // Save to a temporary file
    const tempFile = path.join(__dirname, "test_output.mp3")
    fs.writeFileSync(tempFile, audioBuffer)
    console.log(`Audio saved to: ${tempFile}`)

    // Play the audio
    console.log("Playing audio...")

    if (process.platform === "win32") {
      // Windows
      await execAsync(`powershell -c (New-Object Media.SoundPlayer '${tempFile}').PlaySync()`)
    } else if (process.platform === "darwin") {
      // macOS
      await execAsync(`afplay '${tempFile}'`)
    } else {
      // Linux
      await execAsync(`mpg123 '${tempFile}'`)
    }

    console.log("Test completed successfully")
  } catch (error) {
    console.error("Error testing Nigerian voice:", error)
    process.exit(1)
  }
}

main()

