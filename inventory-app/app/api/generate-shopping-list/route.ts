import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Get backend URL from environment variable
    const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_BACKEND_API_URL

    if (!backendUrl) {
      console.error("BACKEND_API_URL not configured")
      // Return mock data if backend not configured
      const mockShoppingList = {
        shopping_list: {
          items: [
            { name: "Backend Not Configured", quantity: "Please set BACKEND_API_URL" },
          ],
          total: 1
        },
        current_inventory: {
          items: [],
          total: 0
        }
      }
      return NextResponse.json(mockShoppingList)
    }

    // Forward the request to your Flask backend
    const response = await fetch(`${backendUrl}/api/generate-shopping-list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error("Error generating shopping list:", error)
    return NextResponse.json({ 
      error: "Failed to generate shopping list",
      details: error instanceof Error ? error.message : "Unknown error"
    }, { status: 500 })
  }
}

export const runtime = 'edge'
