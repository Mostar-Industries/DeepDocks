// Add speech initialization if needed
import type React from "react"
import { DeepCALChat } from "@/components/DeepCALChat"
import "./globals.css"

// In React Server Components, we can't use hooks directly
// so we'll use a client component for initialization

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        {/* Add the chat interface here */}
        <DeepCALChat />
      </body>
    </html>
  )
}

