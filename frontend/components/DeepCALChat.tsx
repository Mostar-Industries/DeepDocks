"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  MessageCircle,
  X,
  Send,
  Mic,
  Volume2,
  AlertTriangle,
  Sparkles,
  Bot,
  User,
  Maximize2,
  Minimize2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

// Import voice functionality
import { useVoice } from "@/hooks/use-voice"
import { useAnomalyDetection } from "@/hooks/use-anomaly-detection"

interface Message {
  id: string
  content: string
  sender: "user" | "system"
  timestamp: Date
  isAlert?: boolean
  alertLevel?: "info" | "warning" | "critical"
}

export function DeepCALChat() {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(isExpanded)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const [voiceEnabled, setVoiceEnabled] = useState(true)

  // Custom hooks for voice and anomaly detection
  const {
    speak,
    stopSpeaking,
    startListening,
    stopListening,
    transcript,
    isSpeaking: voiceIsSpeaking,
    isLoading,
    error: voiceError,
  } = useVoice({
    onStart: () => setIsSpeaking(true),
    onEnd: () => setIsSpeaking(false),
    onError: (error) => console.error("Speech error:", error),
  })
  const { anomalies, registerAnomalyHandler } = useAnomalyDetection()

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Handle transcript changes
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript)
    }
  }, [transcript])

  // Handle anomalies
  useEffect(() => {
    const handleAnomaly = (anomaly: any) => {
      const newMessage: Message = {
        id: `alert-${Date.now()}`,
        content: `ALERT: ${anomaly.message}`,
        sender: "system",
        timestamp: new Date(),
        isAlert: true,
        alertLevel: anomaly.level,
      }

      setMessages((prev) => [...prev, newMessage])

      // Automatically open chat on critical alerts
      if (anomaly.level === "critical") {
        setIsOpen(true)

        // Speak the alert
        speak(`Alert: ${anomaly.message}`)
      }
    }

    // Register handler
    registerAnomalyHandler(handleAnomaly)

    // Initial welcome message
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: `system-${Date.now()}`,
        content: "Welcome to DeepCAL++. How can I assist with your logistics operations today?",
        sender: "system",
        timestamp: new Date(),
      }

      setMessages([welcomeMessage])
    }

    return () => {
      // Cleanup
      stopSpeaking()
      stopListening()
    }
  }, [])

  // Update the useEffect for initialization to require user interaction

  // Initialize speech synthesis
  useEffect(() => {
    // We'll initialize speech synthesis only when the chat is opened
    // This ensures there's user interaction before attempting speech
    const initSpeechSynthesis = () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        try {
          // Some browsers require a user interaction before allowing speech synthesis
          // This dummy utterance helps initialize the system
          const utterance = new SpeechSynthesisUtterance("")
          window.speechSynthesis.speak(utterance)
          window.speechSynthesis.cancel() // Cancel it immediately

          // Load voices
          window.speechSynthesis.getVoices()

          console.log("Speech synthesis initialized")
        } catch (e) {
          console.warn("Failed to initialize speech synthesis:", e)
        }
      }
    }

    // Only initialize when chat is opened (ensuring user interaction)
    if (isOpen) {
      initSpeechSynthesis()

      // Add welcome message if there are no messages
      if (messages.length === 0) {
        const welcomeMessage: Message = {
          id: `system-${Date.now()}`,
          content: "Welcome to DeepCAL++. How can I assist with your logistics operations today?",
          sender: "system",
          timestamp: new Date(),
        }

        setMessages([welcomeMessage])

        // Don't automatically speak the welcome message
        // Let the user trigger voice by interacting first
      }
    }

    return () => {
      // Cleanup speech synthesis
      stopSpeaking()
      stopListening()
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel()
      }
    }
  }, [isOpen]) // Dependency on isOpen ensures this runs when chat is opened

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])

    // Process the message and generate a response
    processMessage(inputValue)

    // Clear input
    setInputValue("")

    // Focus input
    inputRef.current?.focus()
  }

  const processMessage = async (message: string) => {
    // In a real implementation, this would call your backend API
    // For now, we'll simulate a response

    // Simulate typing delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Generate response
    const response = `I've processed your request: "${message}". The optimal logistics route has been calculated with 95% confidence.`

    // Add system message
    const systemMessage: Message = {
      id: `system-${Date.now()}`,
      content: response,
      sender: "system",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, systemMessage])

    // Speak the response with error handling
    if (voiceEnabled) {
      try {
        await speak(response)
      } catch (error) {
        console.error("Error speaking response:", error)
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const toggleListening = () => {
    if (isListening) {
      stopListening()
      setIsListening(false)
    } else {
      startListening()
      setIsListening(true)
    }
  }

  const clearMessages = () => {
    setMessages([])

    // Add welcome message
    const welcomeMessage: Message = {
      id: `system-${Date.now()}`,
      content: "Chat history cleared. How can I assist you?",
      sender: "system",
      timestamp: new Date(),
    }

    setMessages([welcomeMessage])
  }

  const toggleVoice = () => {
    if (voiceIsSpeaking) {
      stopSpeaking()
    }
    setVoiceEnabled(!voiceEnabled)
  }

  return (
    <>
      {/* Floating chat button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={() => setIsOpen(true)}
                    size="lg"
                    className="h-14 w-14 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
                  >
                    <motion.div
                      animate={{
                        scale: [1, 1.1, 1],
                      }}
                      transition={{
                        repeat: Number.POSITIVE_INFINITY,
                        duration: 2,
                      }}
                    >
                      <MessageCircle className="h-6 w-6 text-white" />
                    </motion.div>

                    {/* Notification indicator */}
                    {anomalies.length > 0 && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 flex items-center justify-center text-xs font-bold text-white"
                      >
                        {anomalies.length}
                      </motion.div>
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="left">
                  <p>Open DeepCAL++ Assistant</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat interface */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className={cn(
              "fixed z-50 flex flex-col bg-black/80 backdrop-blur-md border border-blue-500/30 shadow-2xl shadow-blue-500/20 text-white",
              isExpanded ? "inset-4 rounded-xl" : "bottom-6 right-6 w-96 h-[32rem] rounded-2xl",
            )}
          >
            {/* Chat header */}
            <div className="flex items-center justify-between p-4 border-b border-blue-500/30">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Bot className="h-6 w-6 text-blue-400" />
                  <motion.div
                    animate={{
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                      repeat: Number.POSITIVE_INFINITY,
                      duration: 1.5,
                    }}
                    className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-blue-500"
                  />
                </div>
                <div>
                  <h3 className="font-bold text-blue-400">DeepCAL++ Assistant</h3>
                  <p className="text-xs text-blue-300">Logistics Intelligence System</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="h-8 w-8 text-gray-400 hover:text-white hover:bg-blue-950/50"
                >
                  {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 text-gray-400 hover:text-white hover:bg-blue-950/50"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Chat messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <AnimatePresence initial={false}>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={cn("flex gap-3 max-w-[90%]", message.sender === "user" ? "ml-auto" : "mr-auto")}
                  >
                    {message.sender === "system" && (
                      <div className="h-8 w-8 rounded-full bg-blue-950 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-blue-400" />
                      </div>
                    )}

                    <div
                      className={cn(
                        "rounded-2xl p-3",
                        message.sender === "user"
                          ? "bg-blue-600 text-white"
                          : message.isAlert
                            ? message.alertLevel === "critical"
                              ? "bg-red-950/70 border border-red-500/50"
                              : message.alertLevel === "warning"
                                ? "bg-yellow-950/70 border border-yellow-500/50"
                                : "bg-blue-950/70 border border-blue-500/50"
                            : "bg-blue-950/70 border border-blue-500/50",
                      )}
                    >
                      {message.isAlert && (
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle
                            className={cn(
                              "h-4 w-4",
                              message.alertLevel === "critical"
                                ? "text-red-400"
                                : message.alertLevel === "warning"
                                  ? "text-yellow-400"
                                  : "text-blue-400",
                            )}
                          />
                          <Badge
                            className={cn(
                              "text-xs",
                              message.alertLevel === "critical"
                                ? "bg-red-600"
                                : message.alertLevel === "warning"
                                  ? "bg-yellow-600"
                                  : "bg-blue-600",
                            )}
                          >
                            {message.alertLevel === "critical"
                              ? "CRITICAL ALERT"
                              : message.alertLevel === "warning"
                                ? "WARNING"
                                : "INFORMATION"}
                          </Badge>
                        </div>
                      )}

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
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Auto-scroll anchor */}
              <div ref={messagesEndRef} />

              {/* Typing indicator */}
              {voiceIsSpeaking && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-blue-400 text-sm"
                >
                  <motion.div
                    animate={{
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      repeat: Number.POSITIVE_INFINITY,
                      duration: 1.5,
                    }}
                  >
                    <Volume2 className="h-4 w-4" />
                  </motion.div>
                  <span>DeepCAL++ is speaking...</span>
                </motion.div>
              )}
              {voiceError && (
                <div className="flex items-center gap-2 text-red-400 text-sm bg-red-950/30 p-2 rounded-lg">
                  <AlertTriangle className="h-4 w-4" />
                  <span>Voice error: {voiceError}</span>
                </div>
              )}
            </div>

            {/* Chat input */}
            <div className="p-4 border-t border-blue-500/30">
              <div className="relative">
                <Textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message..."
                  className="min-h-12 pr-24 bg-blue-950/30 border-blue-500/30 focus:border-blue-500 resize-none text-white placeholder:text-gray-400"
                  rows={2}
                />

                <div className="absolute bottom-2 right-2 flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleListening}
                    className={cn(
                      "h-8 w-8 rounded-full",
                      isListening
                        ? "bg-red-500 text-white hover:bg-red-600"
                        : "text-gray-400 hover:text-white hover:bg-blue-950/50",
                    )}
                  >
                    <Mic className="h-4 w-4" />
                  </Button>

                  <Button
                    onClick={handleSendMessage}
                    size="icon"
                    className="h-8 w-8 rounded-full bg-blue-600 text-white hover:bg-blue-700"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Additional controls */}
              <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearMessages}
                  className="h-6 px-2 text-xs text-gray-400 hover:text-white hover:bg-blue-950/50"
                >
                  Clear Chat
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleVoice}
                  className="h-6 px-2 text-xs text-gray-400 hover:text-white hover:bg-blue-950/50"
                >
                  {voiceEnabled ? "Disable Voice" : "Enable Voice"}
                </Button>

                <div className="flex items-center gap-1">
                  <Sparkles className="h-3 w-3 text-blue-400" />
                  <span>Powered by DeepCAL++ Intelligence</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

