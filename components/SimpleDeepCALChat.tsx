"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { X, Send, Mic, Bot, User, MessageCircle, Volume2, VolumeX, AlertTriangle } from "lucide-react"

export function SimpleDeepCALChat() {
  const [isOpen, setIsOpen] = useState(false)
  const [userName, setUserName] = useState<string | null>(null)
  const [messages, setMessages] = useState<
    Array<{
      id: string
      content: string
      sender: "user" | "system"
      timestamp: Date
      isAlert?: boolean
    }>
  >([
    {
      id: "welcome",
      content:
        "Welcome to Deep Cal — where freight decisions meet math, mayhem, and a mildly over-caffeinated algorithm. Let's calculate brilliance. But one thing at a time... Start by telling me your name, boss.",
      sender: "system",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [voiceError, setVoiceError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Initialize speech synthesis
  useEffect(() => {
    // Speak the welcome message
    if (voiceEnabled) {
      speakText(messages[0].content)
    }

    return () => {
      // Stop any speaking when component unmounts
      stopSpeaking()
    }
  }, [])

  // Function to speak text using browser's speech synthesis
  const speakText = (text: string) => {
    if (!voiceEnabled || typeof window === "undefined") return

    try {
      setIsSpeaking(true)
      setVoiceError(null)

      // Check if speech synthesis is available
      if ("speechSynthesis" in window) {
        // Stop any current speech
        window.speechSynthesis.cancel()

        // Create a new utterance
        const utterance = new SpeechSynthesisUtterance(text)

        // Set properties
        utterance.rate = 1.0
        utterance.pitch = 1.0
        utterance.volume = 1.0

        // Set event handlers
        utterance.onend = () => setIsSpeaking(false)
        utterance.onerror = (e) => {
          console.error("Speech synthesis error:", e)
          setIsSpeaking(false)
          setVoiceError("Failed to speak text")
        }

        // Try to find a good voice
        if (window.speechSynthesis.getVoices().length > 0) {
          // Prefer a female voice for the assistant
          const voices = window.speechSynthesis.getVoices()
          const femaleVoice = voices.find(
            (voice) =>
              voice.name.includes("female") ||
              voice.name.includes("Samantha") ||
              voice.name.includes("Google UK English Female"),
          )

          if (femaleVoice) {
            utterance.voice = femaleVoice
          }
        }

        // Speak the text
        window.speechSynthesis.speak(utterance)
      } else {
        console.warn("Speech synthesis not supported")
        setIsSpeaking(false)
        setVoiceError("Speech synthesis not supported in this browser")
      }
    } catch (error) {
      console.error("Error in speech synthesis:", error)
      setIsSpeaking(false)
      setVoiceError("Error in speech synthesis")
    }
  }

  // Function to stop speaking
  const stopSpeaking = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel()
    }

    setIsSpeaking(false)
  }

  // Toggle voice
  const toggleVoice = () => {
    if (isSpeaking) {
      stopSpeaking()
    }
    setVoiceEnabled(!voiceEnabled)
  }

  // Add humor to responses
  const addHumor = (baseResponse: string): string => {
    const humorousAdditions = [
      " I calculated that faster than a caffeinated logistics manager on a Monday!",
      " If logistics were a sport, this would definitely be a gold medal solution.",
      " I'd bet my last processing cycle that this is the optimal route.",
      " My circuits are practically glowing with pride at this recommendation.",
      " This analysis is so precise, even my debugging module is impressed.",
      " I've analyzed more routes than there are stars in the Milky Way... well, almost.",
      " This solution is so elegant, it deserves its own logistics award.",
      " If I had a physical form, I'd be giving you a thumbs up right now.",
      " My quantum logistics algorithm is practically doing a victory dance.",
      " This recommendation is fresher than newly written code!",
    ]

    // Only add humor 40% of the time to keep it professional
    if (Math.random() < 0.4) {
      return baseResponse + humorousAdditions[Math.floor(Math.random() * humorousAdditions.length)]
    }

    return baseResponse
  }

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      content: inputValue,
      sender: "user" as const,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])

    // Check if this is the name response
    if (!userName) {
      // Extract name from input
      const name = inputValue.trim().split(" ")[0] // Get first word as name
      setUserName(name)

      // Respond with personalized greeting
      setTimeout(() => {
        const greeting = `It's a pleasure to meet you, ${name}! I'm Deep Cal Plus Plus, your logistics intelligence assistant. How can I help optimize your logistics operations today?`

        const systemMessage = {
          id: `system-${Date.now()}`,
          content: greeting,
          sender: "system" as const,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, systemMessage])

        // Speak the greeting
        if (voiceEnabled) {
          speakText(greeting)
        }
      }, 1000)
    } else {
      // Regular response
      setTimeout(() => {
        // Generate base response
        const baseResponses = [
          `I've calculated the optimal logistics route for your shipment with 95% confidence.`,
          `Based on historical data, the most reliable carrier for this route is ExpressShip.`,
          `Your shipment from Kenya to DR Congo should take approximately 14 days via air freight.`,
          `I've analyzed 7 potential carriers and ranked them based on cost, time, and reliability.`,
          `The TOPSIS analysis indicates AfricaLogistics offers the best balance of factors for your needs.`,
          `${userName}, I've found three potential routes for your shipment, with varying cost-time tradeoffs.`,
          `My analysis shows a 23% cost saving opportunity if you're flexible with delivery time.`,
          `I've detected a potential customs clearance issue with your selected route. Would you like alternatives?`,
        ]

        const baseResponse = baseResponses[Math.floor(Math.random() * baseResponses.length)]

        // Add humor to the response
        const response = addHumor(baseResponse)

        // Add system message
        const systemMessage = {
          id: `system-${Date.now()}`,
          content: response,
          sender: "system" as const,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, systemMessage])

        // Speak the response
        if (voiceEnabled) {
          speakText(response)
        }
      }, 1000)
    }

    // Clear input
    setInputValue("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Simulate an alert after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      const alertMessage = {
        id: `alert-${Date.now()}`,
        content: `ALERT: Data completeness below threshold for Nigeria-Ghana route${userName ? `, ${userName}` : ""}. This may affect prediction accuracy.`,
        sender: "system" as const,
        timestamp: new Date(),
        isAlert: true,
      }

      setMessages((prev) => [...prev, alertMessage])

      // Open chat when alert is received
      setIsOpen(true)

      // Speak the alert
      if (voiceEnabled) {
        speakText(alertMessage.content)
      }
    }, 8000) // Increased to 8 seconds to give time for name interaction

    return () => clearTimeout(timer)
  }, [userName, voiceEnabled])

  return (
    <>
      {/* Floating chat button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg flex items-center justify-center hover:shadow-blue-500/40 transition-shadow"
        >
          <div className="animate-pulse">
            <MessageCircle className="h-6 w-6 text-white" />
          </div>
        </button>
      )}

      {/* Chat interface */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[32rem] rounded-2xl z-50 flex flex-col bg-black/80 backdrop-blur-md border border-blue-500/30 shadow-2xl shadow-blue-500/20 text-white">
          {/* Chat header */}
          <div className="flex items-center justify-between p-4 border-b border-blue-500/30">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Bot className="h-6 w-6 text-blue-400" />
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
              </div>
              <div>
                <h3 className="font-bold text-blue-400">Deep Cal Assistant</h3>
                <p className="text-xs text-blue-300">
                  {userName ? `Assisting ${userName}` : "Logistics Intelligence System"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={toggleVoice}
                className="h-8 w-8 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-blue-950/50"
                title={voiceEnabled ? "Disable voice" : "Enable voice"}
              >
                {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </button>

              <button
                onClick={() => setIsOpen(false)}
                className="h-8 w-8 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-blue-950/50"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 max-w-[90%] ${message.sender === "user" ? "ml-auto" : "mr-auto"}`}
              >
                {message.sender === "system" && (
                  <div className="h-8 w-8 rounded-full bg-blue-950 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-blue-400" />
                  </div>
                )}

                <div
                  className={`rounded-2xl p-3 ${
                    message.sender === "user"
                      ? "bg-blue-600 text-white"
                      : message.isAlert
                        ? "bg-red-950/70 border border-red-500/50"
                        : "bg-blue-950/70 border border-blue-500/50"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>

                  <div className="mt-1 text-right">
                    <span className="text-xs opacity-70">
                      {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>

                {message.sender === "user" && (
                  <div className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-gray-300" />
                  </div>
                )}
              </div>
            ))}

            {/* Voice error message */}
            {voiceError && (
              <div className="flex items-center gap-2 text-red-400 text-sm bg-red-950/30 p-2 rounded-lg">
                <AlertTriangle className="h-4 w-4" />
                <span>Voice error: {voiceError}</span>
              </div>
            )}

            {/* Speaking indicator */}
            {isSpeaking && (
              <div className="flex items-center gap-2 text-blue-400 text-sm">
                <Volume2 className="h-4 w-4 animate-pulse" />
                <span>Deep Cal is speaking...</span>
              </div>
            )}

            {/* Auto-scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat input */}
          <div className="p-4 border-t border-blue-500/30">
            <div className="relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={userName ? "Type your message..." : "Please enter your name..."}
                className="min-h-12 w-full pr-24 p-3 bg-blue-950/30 border border-blue-500/30 focus:border-blue-500 rounded-lg resize-none text-white placeholder:text-gray-400 outline-none"
                rows={2}
              />

              <div className="absolute bottom-2 right-2 flex items-center gap-2">
                <button className="h-8 w-8 rounded-full flex items-center justify-center text-gray-400 hover:text-white hover:bg-blue-950/50">
                  <Mic className="h-4 w-4" />
                </button>

                <button
                  onClick={handleSendMessage}
                  className="h-8 w-8 rounded-full bg-blue-600 text-white hover:bg-blue-700 flex items-center justify-center"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Additional controls */}
            <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
              <button
                onClick={() => {
                  stopSpeaking()
                  setUserName(null)
                  setVoiceError(null)
                  setMessages([
                    {
                      id: "welcome",
                      content:
                        "Welcome to Deep Cal — where freight decisions meet math, mayhem, and a mildly over-caffeinated algorithm. Let's calculate brilliance. But one thing at a time... Start by telling me your name, boss.",
                      sender: "system",
                      timestamp: new Date(),
                    },
                  ])
                  if (voiceEnabled) {
                    setTimeout(() => {
                      speakText(
                        "Welcome to Deep Cal — where freight decisions meet math, mayhem, and a mildly over-caffeinated algorithm. Let's calculate brilliance. But one thing at a time... Start by telling me your name, boss.",
                      )
                    }, 100)
                  }
                }}
                className="h-6 px-2 text-xs text-gray-400 hover:text-white hover:bg-blue-950/50 rounded"
              >
                Reset Chat
              </button>

              <div className="flex items-center gap-1">
                <span>Powered by Deep Cal Intelligence</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

