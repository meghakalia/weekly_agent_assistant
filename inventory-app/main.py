from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import uvicorn

app = FastAPI(title="Inventory Management API", version="1.0.0")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class InventoryItem(BaseModel):
    name: str
    quantity: int
    unit: str
    category: str
    expiry_date: str = None

class InventoryResponse(BaseModel):
    date: str
    items: List[InventoryItem]

class ShoppingListItem(BaseModel):
    name: str
    quantity: int
    unit: str
    category: str
    priority: str = "medium"

class ShoppingListRequest(BaseModel):
    inventory_data: dict

class ShoppingListResponse(BaseModel):
    items: List[ShoppingListItem]

def process_image_to_inventory(image_data: bytes) -> InventoryResponse:
    """
    Process uploaded image and extract inventory information.
    Replace this with your actual AI/ML processing logic.
    """
    # Mock inventory data - replace with actual image processing
    mock_inventory = InventoryResponse(
        date=datetime.now().strftime("%Y-%m-%d"),
        items=[
            InventoryItem(
                name="Milk",
                quantity=1,
                unit="bottle",
                category="dairy",
                expiry_date="2024-01-15"
            ),
            InventoryItem(
                name="Bread",
                quantity=2,
                unit="loaves",
                category="bakery",
                expiry_date="2024-01-10"
            ),
            InventoryItem(
                name="Eggs",
                quantity=12,
                unit="pieces",
                category="dairy",
                expiry_date="2024-01-20"
            ),
            InventoryItem(
                name="Apples",
                quantity=6,
                unit="pieces",
                category="fruits",
                expiry_date="2024-01-18"
            ),
            InventoryItem(
                name="Rice",
                quantity=1,
                unit="kg",
                category="grains"
            )
        ]
    )
    
    return mock_inventory

def generate_shopping_suggestions(inventory_data: dict) -> ShoppingListResponse:
    """
    Generate shopping list based on inventory data.
    Replace this with your actual recommendation logic.
    """
    # Mock shopping list - replace with actual logic
    mock_shopping_list = ShoppingListResponse(
        items=[
            ShoppingListItem(
                name="Milk",
                quantity=2,
                unit="bottles",
                category="dairy",
                priority="high"
            ),
            ShoppingListItem(
                name="Bread",
                quantity=1,
                unit="loaf",
                category="bakery",
                priority="medium"
            ),
            ShoppingListItem(
                name="Bananas",
                quantity=1,
                unit="bunch",
                category="fruits",
                priority="low"
            ),
            ShoppingListItem(
                name="Chicken",
                quantity=1,
                unit="kg",
                category="meat",
                priority="high"
            ),
            ShoppingListItem(
                name="Yogurt",
                quantity=4,
                unit="cups",
                category="dairy",
                priority="medium"
            )
        ]
    )
    
    return mock_shopping_list

@app.get("/")
async def root():
    return {"message": "Inventory Management API is running!"}

@app.post("/api/process-inventory", response_model=InventoryResponse)
async def process_inventory(file: UploadFile = File(...)):
    """
    Process uploaded image and return inventory information.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Validate image can be opened
        try:
            image = Image.open(BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Process image and get inventory
        inventory_result = process_image_to_inventory(image_data)
        
        return inventory_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/api/generate-shopping-list", response_model=ShoppingListResponse)
async def generate_shopping_list(request: ShoppingListRequest):
    """
    Generate shopping list based on inventory data.
    """
    try:
        # Generate shopping suggestions
        shopping_list = generate_shopping_suggestions(request.inventory_data)
        
        return shopping_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shopping list: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
