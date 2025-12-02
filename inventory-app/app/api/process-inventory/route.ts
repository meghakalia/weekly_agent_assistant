import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const image = formData.get("image") as File

    if (!image) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 })
    }

    // Get backend URL from environment variable
    const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_BACKEND_API_URL

    if (!backendUrl) {
      console.error("BACKEND_API_URL not configured")
      // Return mock data if backend not configured
      const mockResponse = {
        date: new Date().toISOString().split("T")[0],
        items: [
          { name: "Backend Not Configured", quantity: "Please set BACKEND_API_URL" },
        ],
      }
      return NextResponse.json(mockResponse)
    }

    // Forward the request to your Flask backend
    const backendFormData = new FormData()
    backendFormData.append("image", image)

    const response = await fetch(`${backendUrl}/process-inventory`, {
      method: "POST",
      body: backendFormData,
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error("Error processing inventory:", error)
    return NextResponse.json({ 
      error: "Failed to process inventory", 
      details: error instanceof Error ? error.message : "Unknown error"
    }, { status: 500 })
  }
}

export const runtime = 'edge'
