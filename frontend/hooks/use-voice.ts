"use client"

import { useState, useEffect, useCallback } from "react"

interface VoiceOptions {
  autoplay?: boolean
  onStart?: () => void
  onEnd?: () => void
  onError?: (error: string) => void
}

export function useVoice(options: VoiceOptions = {}) {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [transcript, setTranscript] = useState("")
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

  // Initialize audio element
  useEffect(() => {
    if (typeof window !== "undefined") {
      const audio = new Audio()

      audio.onplay = () => {
        setIsSpeaking(true)
        options.onStart?.()
      }

      audio.onended = () => {
        setIsSpeaking(false)
        options.onEnd?.()
      }

      audio.onerror = () => {
        setIsSpeaking(false)
        setError("Failed to play audio")
        options.onError?.("Failed to play audio")
      }

      setAudioElement(audio)
    }

    return () => {
      if (audioElement) {
        audioElement.pause()
        audioElement.src = ""
      }
    }
  }, [])

  // Function to speak text
  const speak = useCallback(
    async (text: string) => {
      if (!text) return false

      try {
        setIsLoading(true)
        setError(null)

        // Stop any current speech
        stopSpeaking()

        // First try browser's built-in speech synthesis as a fallback
        if (typeof window !== "undefined" && "speechSynthesis" in window) {
          try {
            // Create a new utterance
            const utterance = new SpeechSynthesisUtterance(text)

            // Try to find a suitable voice
            const voices = window.speechSynthesis.getVoices()
            // Look for a Nigerian voice as first preference, or any English voice as fallback
            const nigerianVoice = voices.find((v) => v.lang.includes("en-NG") || v.name.includes("Nigerian"))
            const englishVoice = voices.find((v) => v.lang.includes("en-") || v.name.includes("English"))

            if (nigerianVoice) {
              utterance.voice = nigerianVoice
            } else if (englishVoice) {
              utterance.voice = englishVoice
            }

            // Set up event handlers
            utterance.onstart = () => {
              setIsSpeaking(true)
              options.onStart?.()
            }

            utterance.onend = () => {
              setIsSpeaking(false)
              options.onEnd?.()
            }

            utterance.onerror = (e) => {
              console.warn("Browser speech synthesis error:", e)
              setIsSpeaking(false)
              setError("Browser speech synthesis failed")
              options.onError?.("Browser speech synthesis failed")

              // Don't try server API here - just return false
              setIsLoading(false)
            }

            // Try browser speech synthesis
            window.speechSynthesis.speak(utterance)
            setIsLoading(false)
            return true
          } catch (browserSpeechError) {
            console.warn("Browser speech synthesis failed:", browserSpeechError)
            // Fall through to server API
          }
        }

        // Call our API to get the speech audio
        const response = await fetch("/api/voice/speak", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
        })

        if (!response.ok) {
          throw new Error(`Failed to generate speech: ${response.status}`)
        }

        // Get the audio blob
        const audioBlob = await response.blob()

        // Create object URL
        const audioUrl = URL.createObjectURL(audioBlob)

        // Set the audio source and event handlers
        if (audioElement) {
          audioElement.src = audioUrl

          // Make sure event handlers are set
          audioElement.onplay = () => {
            setIsSpeaking(true)
            options.onStart?.()
          }

          audioElement.onended = () => {
            setIsSpeaking(false)
            options.onEnd?.()
          }

          audioElement.onerror = () => {
            setIsSpeaking(false)
            setError("Failed to play audio")
            options.onError?.("Failed to play audio")
          }

          // Play the audio
          try {
            await audioElement.play()
          } catch (playError) {
            console.error("Error playing audio:", playError)
            setError("Failed to play audio: " + (playError instanceof Error ? playError.message : "Unknown error"))
            options.onError?.("Failed to play audio")
            setIsLoading(false)
            return false
          }
        }

        setIsLoading(false)
        return true
      } catch (error) {
        console.error("Error speaking text:", error)
        setIsLoading(false)
        setError(error instanceof Error ? error.message : "Unknown error")
        options.onError?.(error instanceof Error ? error.message : "Unknown error")
        return false
      }
    },
    [audioElement, options],
  )

  // Function to stop speaking
  const stopSpeaking = useCallback(() => {
    // First try to stop browser speech synthesis
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel()
    }

    // Then stop our audio element
    if (!audioElement) return false

    try {
      audioElement.pause()
      audioElement.currentTime = 0
      setIsSpeaking(false)
      return true
    } catch (error) {
      console.error("Error stopping speech:", error)
      return false
    }
  }, [audioElement])

  // Function to start listening (placeholder for future implementation)
  const startListening = useCallback(() => {
    setTranscript("")
    // This would be implemented with a speech recognition API
    return true
  }, [])

  // Function to stop listening (placeholder for future implementation)
  const stopListening = useCallback(() => {
    // This would be implemented with a speech recognition API
    return true
  }, [])

  return {
    speak,
    stopSpeaking,
    startListening,
    stopListening,
    transcript,
    isSpeaking,
    isLoading,
    error,
  }
}

