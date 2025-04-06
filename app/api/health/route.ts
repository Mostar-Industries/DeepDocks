import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"
import { validateEnv } from "@/utils/env_check"

export async function GET(request: NextRequest) {
  try {
    // Check for API key in request
    const authHeader = request.headers.get("Authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const token = authHeader.substring(7)
    const apiKey = process.env.DEEPCAL_API_KEY

    if (!apiKey || token !== apiKey) {
      return NextResponse.json({ error: "Invalid API key" }, { status: 401 })
    }

    // Check environment variables
    const envCheck = validateEnv()

    // Path to the Python script
    const pythonScriptPath = path.join(process.cwd(), "backend", "cli", "check_status.py")

    // Spawn Python process
    const pythonProcess = spawn("python", [pythonScriptPath, "--format", "json", "--no-personality"])

    // Collect output from Python process
    let outputData = ""
    let errorData = ""

    pythonProcess.stdout.on("data", (data) => {
      outputData += data.toString()
    })

    pythonProcess.stderr.on("data", (data) => {
      errorData += data.toString()
    })

    // Wait for Python process to complete
    const exitCode = await new Promise((resolve) => {
      pythonProcess.on("close", resolve)
    })

    // Check for errors
    if (exitCode !== 0) {
      console.error("Python process error:", errorData)
      return NextResponse.json(
        {
          error: "Failed to run health check",
          details: errorData,
          env_check: envCheck,
        },
        { status: 500 },
      )
    }

    try {
      // Parse the output as JSON
      const results = JSON.parse(outputData)

      // Add environment check results
      results.env_check = envCheck

      return NextResponse.json(results)
    } catch (parseError) {
      console.error("Error parsing Python output:", parseError)
      console.error("Raw output:", outputData)
      return NextResponse.json(
        {
          error: "Failed to parse health check results",
          details: parseError.message,
          env_check: envCheck,
        },
        { status: 500 },
      )
    }
  } catch (error) {
    console.error("Error running health check:", error)
    return NextResponse.json({ error: "Failed to run health check" }, { status: 500 })
  }
}

