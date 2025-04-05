/**
 * DeepCAL++ Voice Module
 * This module provides text-to-speech functionality using a Nigerian male voice
 */
import { generateSpeech, getVoiceStats, clearVoiceCache } from "./nigerian_voice_service"
import fs from "fs"
import path from "path"
import { promisify } from "util"
import { exec } from "child_process"
import os from "os"

// Promisify exec
const execAsync = promisify(exec)

// Track speaking state
let isSpeaking = false
let currentProcess: any = null

/**
 * Speak text using the Nigerian male voice
 *
 * @param text - Text to speak
 * @param blocking - Whether to block until speech is complete
 * @param speed - Speech rate multiplier (0.5 to 2.0)
 * @returns True if speech started successfully, False otherwise
 */
export async function speak_text(text: string, blocking = false, speed = 1.0): Promise<boolean> {
  if (!text) return false

  try {
    // Stop any current speech
    stop_speaking()

    // Generate speech
    const audioBuffer = await generateSpeech(text)
    if (!audioBuffer) {
      console.error("Failed to generate speech")
      return false
    }

    // Create a temporary file for the audio
    const tempDir = os.tmpdir()
    const tempFile = path.join(tempDir, `deepcal_speech_${Date.now()}.mp3`)
    fs.writeFileSync(tempFile, audioBuffer)

    // Play the audio
    isSpeaking = true

    if (process.platform === "win32") {
      // Windows
      currentProcess = execAsync(`powershell -c (New-Object Media.SoundPlayer '${tempFile}').PlaySync()`)
    } else if (process.platform === "darwin") {
      // macOS
      currentProcess = execAsync(`afplay '${tempFile}'`)
    } else {
      // Linux
      currentProcess = execAsync(`mpg123 '${tempFile}'`)
    }

    if (blocking) {
      // Wait for the process to complete
      await currentProcess
      isSpeaking = false

      // Clean up temp file
      try {
        fs.unlinkSync(tempFile)
      } catch (error) {
        console.error("Error removing temp file:", error)
      }
    } else {
      // Clean up when done in non-blocking mode
      currentProcess
        .then(() => {
          isSpeaking = false
          try {
            fs.unlinkSync(tempFile)
          } catch (error) {
            console.error("Error removing temp file:", error)
          }
        })
        .catch((error: any) => {
          console.error("Error playing audio:", error)
          isSpeaking = false
          try {
            fs.unlinkSync(tempFile)
          } catch (error) {
            console.error("Error removing temp file:", error)
          }
        })
    }

    return true
  } catch (error) {
    console.error("Error in speak_text:", error)
    isSpeaking = false
    return false
  }
}

/**
 * Stop current speech
 *
 * @returns True if stopped successfully, False otherwise
 */
export function stop_speaking(): boolean {
  if (!isSpeaking || !currentProcess) return false

  try {
    if (process.platform === "win32") {
      // Windows
      execAsync("taskkill /F /IM powershell.exe")
    } else if (process.platform === "darwin") {
      // macOS
      execAsync("killall afplay")
    } else {
      // Linux
      execAsync("killall mpg123")
    }

    isSpeaking = false
    currentProcess = null
    return true
  } catch (error) {
    console.error("Error stopping speech:", error)
    return false
  }
}

/**
 * Check if voice functionality is available
 *
 * @returns True if voice is available, False otherwise
 */
export function check_voice_availability(): boolean {
  return true // Always available with our implementation
}

/**
 * Get voice usage statistics
 *
 * @returns Dictionary with usage statistics
 */
export function get_voice_usage_stats(): any {
  return getVoiceStats()
}

/**
 * Clear the voice cache
 *
 * @returns True if cleared successfully, False otherwise
 */
export function clear_voice_cache(): boolean {
  return clearVoiceCache()
}

