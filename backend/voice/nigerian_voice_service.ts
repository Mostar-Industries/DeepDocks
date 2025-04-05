/**
 * Nigerian Voice Service for DeepCAL++
 *
 * This service provides a high-quality Nigerian male voice using
 * the free Narakeet TTS API with caching for reliability.
 */

import fs from "fs"
import path from "path"
import axios from "axios"
import crypto from "crypto"
import { promisify } from "util"

// Promisify fs functions
const mkdir = promisify(fs.mkdir)
const writeFile = promisify(fs.writeFile)
const readFile = promisify(fs.readFile)
const access = promisify(fs.access)

// Voice configuration
const VOICE_ID = "kingsley" // Nigerian male voice
const VOICE_PROVIDER = "narakeet"
const CACHE_DIR = path.join(process.cwd(), "cache", "voice")

// Ensure cache directory exists
async function ensureCacheDir() {
  try {
    await access(CACHE_DIR)
  } catch (error) {
    await mkdir(CACHE_DIR, { recursive: true })
  }
}

// Generate a cache key for a text
function generateCacheKey(text: string): string {
  return crypto.createHash("md5").update(text).digest("hex")
}

// Get cache path for a text
function getCachePath(text: string): string {
  const cacheKey = generateCacheKey(text)
  return path.join(CACHE_DIR, `${cacheKey}.mp3`)
}

// Check if text is cached
async function isTextCached(text: string): Promise<boolean> {
  const cachePath = getCachePath(text)
  try {
    await access(cachePath, fs.constants.R_OK)
    return true
  } catch (error) {
    return false
  }
}

// Get cached audio for a text
async function getCachedAudio(text: string): Promise<Buffer | null> {
  if (await isTextCached(text)) {
    return readFile(getCachePath(text))
  }
  return null
}

// Cache audio for a text
async function cacheAudio(text: string, audioBuffer: Buffer): Promise<void> {
  await ensureCacheDir()
  const cachePath = getCachePath(text)
  await writeFile(cachePath, audioBuffer)
}

/**
 * Generate speech from text using the Nigerian male voice
 *
 * @param text - The text to convert to speech
 * @param forceFresh - Whether to force fresh generation (bypass cache)
 * @returns Buffer containing the audio data or null if generation failed
 */
export async function generateSpeech(text: string, forceFresh = false): Promise<Buffer | null> {
  if (!text) return null

  try {
    // Check cache first (unless forceFresh is true)
    if (!forceFresh) {
      const cachedAudio = await getCachedAudio(text)
      if (cachedAudio) {
        console.log("Using cached audio for:", text.substring(0, 30) + "...")
        return cachedAudio
      }
    }

    // Generate fresh audio using Narakeet API
    console.log("Generating fresh audio for:", text.substring(0, 30) + "...")

    try {
      // Prepare the API request
      const apiUrl = "https://api.narakeet.com/text-to-speech/mp3"
      const options = {
        method: "POST",
        url: apiUrl,
        params: {
          voice: VOICE_ID,
        },
        headers: {
          "Content-Type": "text/plain",
          Accept: "application/octet-stream",
        },
        data: text,
        responseType: "arraybuffer",
      }

      // Make the API request
      const response = await axios(options)

      if (response.status === 200) {
        // Convert response to Buffer
        const audioBuffer = Buffer.from(response.data)

        // Cache the audio
        await cacheAudio(text, audioBuffer)

        return audioBuffer
      } else {
        console.error("Failed to generate speech:", response.status, response.statusText)
        throw new Error(`API returned status code ${response.status}`)
      }
    } catch (apiError) {
      console.error("Error calling Narakeet API:", apiError)

      // Generate a basic fallback audio file
      // Note: In a real implementation, you might want to use a different
      // fallback TTS service or a pre-generated error message

      // For now, return null to indicate failure
      return null
    }
  } catch (error) {
    console.error("Error generating speech:", error)
    return null
  }
}

/**
 * Get statistics about the voice service
 */
export async function getVoiceStats(): Promise<any> {
  try {
    // Ensure cache directory exists
    await ensureCacheDir()

    // Count cached files
    const files = fs.readdirSync(CACHE_DIR)
    const cacheSize = files.reduce((total, file) => {
      const filePath = path.join(CACHE_DIR, file)
      const stats = fs.statSync(filePath)
      return total + stats.size
    }, 0)

    return {
      provider: VOICE_PROVIDER,
      voice: VOICE_ID,
      cachedPhrases: files.length,
      cacheSize: `${(cacheSize / 1024 / 1024).toFixed(2)} MB`,
    }
  } catch (error) {
    console.error("Error getting voice stats:", error)
    return {
      provider: VOICE_PROVIDER,
      voice: VOICE_ID,
      error: "Failed to get statistics",
    }
  }
}

/**
 * Clear the voice cache
 */
export async function clearVoiceCache(): Promise<boolean> {
  try {
    await ensureCacheDir()
    const files = fs.readdirSync(CACHE_DIR)
    for (const file of files) {
      fs.unlinkSync(path.join(CACHE_DIR, file))
    }
    return true
  } catch (error) {
    console.error("Error clearing voice cache:", error)
    return false
  }
}

