"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Camera, ShoppingCart, Loader2, Package, AlertCircle } from "lucide-react"

interface InventoryItem {
  name: string
  quantity: string
}

interface InventoryData {
  date: string
  items: InventoryItem[]
}

interface ShoppingListData {
  items: InventoryItem[]
}

export default function InventoryApp() {
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [inventoryData, setInventoryData] = useState<InventoryData | null>(null)
  const [shoppingList, setShoppingList] = useState<ShoppingListData | null>(null)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [isProcessingPhoto, setIsProcessingPhoto] = useState(false)
  const [isGeneratingList, setIsGeneratingList] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const checkBackendConnection = async () => {
    try {
      const response = await fetch("http://localhost:8000/health", {
        method: "GET",
        mode: "cors",
      })
      return response.ok
    } catch (error) {
      console.log("[v0] Backend connection failed:", error)
      return false
    }
  }

  const handlePhotoCapture = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setError(null)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setCapturedImage(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    // Convert to JPG and send to backend
    setIsProcessingPhoto(true)

    const isConnected = await checkBackendConnection()
    setBackendConnected(isConnected)

    try {
      // Convert file to JPG format
      const canvas = document.createElement("canvas")
      const ctx = canvas.getContext("2d")
      const img = new Image()

      img.onload = async () => {
        canvas.width = img.width
        canvas.height = img.height
        ctx?.drawImage(img, 0, 0)

        canvas.toBlob(
          async (blob) => {
            if (!blob) return

            const formData = new FormData()
            formData.append("image", blob, "inventory.jpg")

            try {
              if (isConnected) {
                console.log("[v0] Attempting to call backend...")
                const response = await fetch("http://localhost:8000/process-inventory", {
                  method: "POST",
                  mode: "cors",
                  body: formData,
                })

                const data = await response.json()
                console.log("[v0] Backend response received:", data)

                if (!response.ok) {
                  // Backend returned an error
                  const errorMsg = data.error || data.error_details || `Server error: ${response.status}`
                  throw new Error(errorMsg)
                }

                setInventoryData(data)
              } else {
                throw new Error("Backend not available")
              }
            } catch (error) {
              console.error("[v0] Backend error:", error)
              const errorMessage = error instanceof Error ? error.message : String(error)
              setError(`Backend error: ${errorMessage} - Using demo data instead`)

              // Fallback to mock data if backend is not available
              const mockInventoryData: InventoryData = {
                date: new Date().toISOString().split("T")[0],
                items: [
                  { name: "Milk", quantity: "1 gallon" },
                  { name: "Bread", quantity: "2 loaves" },
                  { name: "Eggs", quantity: "1 dozen" },
                  { name: "Chicken Breast", quantity: "2 lbs" },
                  { name: "Rice", quantity: "5 lb bag" },
                  { name: "Pasta", quantity: "3 boxes" },
                  { name: "Olive Oil", quantity: "1 bottle" },
                  { name: "Onions", quantity: "3 lbs" },
                  { name: "Tomatoes", quantity: "2 lbs" },
                  { name: "Cheese", quantity: "1 block" },
                  { name: "Yogurt", quantity: "6 cups" },
                  { name: "Bananas", quantity: "1 bunch" },
                ],
              }
              setInventoryData(mockInventoryData)
            }
            setIsProcessingPhoto(false)
          },
          "image/jpeg",
          0.8,
        )
      }

      img.src = URL.createObjectURL(file)
    } catch (error) {
      console.error("[v0] Error processing image:", error)
      setError("Error processing image")
      setIsProcessingPhoto(false)
    }
  }

  const handleItemSelection = (itemName: string, checked: boolean) => {
    const newSelected = new Set(selectedItems)
    if (checked) {
      newSelected.add(itemName)
    } else {
      newSelected.delete(itemName)
    }
    setSelectedItems(newSelected)
  }

  const generateShoppingList = async () => {
    if (!inventoryData) return

    setError(null)
    setIsGeneratingList(true)

    try {
      const isConnected = await checkBackendConnection()

      if (isConnected) {
        console.log("[v0] Sending shopping list request to backend...")
        const response = await fetch("http://localhost:8000/generate-shopping-list", {
          method: "POST",
          mode: "cors",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            inventory: inventoryData,
            selected_items: Array.from(selectedItems),
          }),
        })

        if (!response.ok) {
          throw new Error(`Backend responded with status: ${response.status}`)
        }

        const data = await response.json()
        console.log("[v0] Shopping list response received:", data)
        setShoppingList(data)
      } else {
        throw new Error("Backend not available")
      }
    } catch (error) {
      console.log("[v0] Using mock shopping list due to backend error:", error)
      setError("Backend not available - using demo shopping list. Please start the Python backend on localhost:8000")

      // Fallback to mock data if backend is not available
      const mockShoppingList: ShoppingListData = {
        items: [
          { name: "Milk", quantity: "2 gallons" },
          { name: "Bread", quantity: "1 loaf" },
          { name: "Eggs", quantity: "2 dozen" },
          { name: "Ground Beef", quantity: "1 lb" },
          { name: "Bell Peppers", quantity: "3 pieces" },
          { name: "Spinach", quantity: "1 bag" },
          { name: "Apples", quantity: "2 lbs" },
          { name: "Cereal", quantity: "2 boxes" },
          { name: "Orange Juice", quantity: "1 carton" },
          { name: "Butter", quantity: "1 pack" },
        ],
      }
      setShoppingList(mockShoppingList)
    }
    setIsGeneratingList(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center py-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Smart Inventory</h1>
          <p className="text-gray-600">Capture your pantry, generate shopping lists</p>
          {backendConnected !== null && (
            <div
              className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm mt-2 ${
                backendConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
              }`}
            >
              <div className={`w-2 h-2 rounded-full ${backendConnected ? "bg-green-500" : "bg-red-500"}`} />
              {backendConnected ? "Backend Connected" : "Backend Offline"}
            </div>
          )}
        </div>

        {error && (
          <Card className="border-2 border-red-200 shadow-lg">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <p className="text-sm">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Photo Capture Section */}
        <Card className="border-2 border-amber-200 shadow-lg">
          <CardHeader className="bg-amber-100">
            <CardTitle className="flex items-center gap-2 text-amber-900">
              <Camera className="w-5 h-5" />
              Capture Inventory
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handlePhotoCapture}
              ref={fileInputRef}
              className="hidden"
            />

            {!capturedImage ? (
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="w-full h-32 bg-amber-500 hover:bg-amber-600 text-white text-lg"
                disabled={isProcessingPhoto}
              >
                <Camera className="w-8 h-8 mr-2" />
                Take Photo of Your Inventory
              </Button>
            ) : (
              <div className="space-y-4">
                <img
                  src={capturedImage || "/placeholder.svg"}
                  alt="Captured inventory"
                  className="w-full h-48 object-cover rounded-lg border-2 border-amber-200"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="w-full border-amber-300 text-amber-700 hover:bg-amber-50"
                >
                  Take Another Photo
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Processing State */}
        {isProcessingPhoto && (
          <Card className="border-2 border-blue-200 shadow-lg">
            <CardContent className="p-6 text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-blue-700 font-medium">Processing your inventory photo...</p>
            </CardContent>
          </Card>
        )}

        {/* Inventory Results */}
        {inventoryData && (
          <Card className="border-2 border-green-200 shadow-lg">
            <CardHeader className="bg-green-100">
              <CardTitle className="flex items-center gap-2 text-green-900">
                <Package className="w-5 h-5" />
                Inventory Detected - {inventoryData.date}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-3">
                {inventoryData.items.map((item, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                    <Checkbox
                      id={`item-${index}`}
                      checked={selectedItems.has(item.name)}
                      onCheckedChange={(checked) => handleItemSelection(item.name, checked as boolean)}
                    />
                    <label htmlFor={`item-${index}`} className="flex-1 cursor-pointer">
                      <span className="font-medium text-green-900">{item.name}</span>
                      <span className="text-green-700 ml-2">({item.quantity})</span>
                    </label>
                  </div>
                ))}
              </div>

              <Button
                onClick={generateShoppingList}
                disabled={isGeneratingList}
                className="w-full mt-6 bg-green-600 hover:bg-green-700 text-white"
              >
                {isGeneratingList ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Generating Shopping List...
                  </>
                ) : (
                  <>
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    Create Shopping List
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Shopping List Results */}
        {shoppingList && (
          <Card className="border-2 border-purple-200 shadow-lg">
            <CardHeader className="bg-purple-100">
              <CardTitle className="flex items-center gap-2 text-purple-900">
                <ShoppingCart className="w-5 h-5" />
                Your Shopping List
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-3">
                {shoppingList.items.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <span className="font-medium text-purple-900">{item.name}</span>
                    <span className="text-purple-700 bg-purple-200 px-2 py-1 rounded-full text-sm">
                      {item.quantity}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
