import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"
import fs from "fs"

export async function POST(request: NextRequest) {
  try {
    // Verify authorization
    const authHeader = request.headers.get("Authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const token = authHeader.substring(7)
    const apiKey = process.env.DEEPCAL_API_KEY

    if (!apiKey || token !== apiKey) {
      return NextResponse.json({ error: "Invalid API key" }, { status: 401 })
    }

    // Get data from request
    const supabaseData = await request.json()

    // Save data to temporary file
    const tempDir = path.join(process.cwd(), "tmp")
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true })
    }

    const tempFile = path.join(tempDir, `mirror_data_${Date.now()}.json`)
    fs.writeFileSync(tempFile, JSON.stringify(supabaseData))

    // Path to the Python script
    const pythonScriptPath = path.join(process.cwd(), "backend", "data", "mirror_data.py")

    // Spawn Python process
    const pythonProcess = spawn("python", [pythonScriptPath, tempFile])

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

    // Clean up temporary file
    try {
      fs.unlinkSync(tempFile)
    } catch (error) {
      console.warn("Error cleaning up temporary file:", error)
    }

    // Check for errors
    if (exitCode !== 0) {
      console.error("Python process error:", errorData)
      return NextResponse.json({ error: "Failed to mirror data", details: errorData }, { status: 500 })
    }

    // Return success response
    return NextResponse.json({
      success: true,
      message: "Data mirrored successfully",
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Error mirroring data:", error)
    return NextResponse.json({ error: "Failed to mirror data" }, { status: 500 })
  }
}

