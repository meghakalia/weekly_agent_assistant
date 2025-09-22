from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class InventoryItem(BaseModel):
    name: str = Field(..., description="Name of the inventory item")
    quantity: int = Field(..., ge=0, description="Quantity of the item")
    unit: str = Field(..., description="Unit of measurement (e.g., pieces, kg, bottles)")
    category: str = Field(..., description="Category of the item (e.g., dairy, fruits, grains)")
    expiry_date: Optional[str] = Field(None, description="Expiry date in YYYY-MM-DD format")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")

class InventoryResponse(BaseModel):
    date: str = Field(..., description="Date when inventory was processed")
    items: List[InventoryItem] = Field(..., description="List of inventory items")
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")

class ShoppingListItem(BaseModel):
    name: str = Field(..., description="Name of the shopping item")
    quantity: int = Field(..., ge=0, description="Recommended quantity to buy")
    unit: str = Field(..., description="Unit of measurement")
    category: str = Field(..., description="Category of the item")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")
    reason: Optional[str] = Field(None, description="Reason for recommendation")

class ShoppingListRequest(BaseModel):
    inventory_data: dict = Field(..., description="Current inventory data")
    preferences: Optional[dict] = Field(None, description="User preferences for shopping")

class ShoppingListResponse(BaseModel):
    items: List[ShoppingListItem] = Field(..., description="List of recommended shopping items")
    total_items: Optional[int] = Field(None, description="Total number of items in the list")
    estimated_cost: Optional[float] = Field(None, description="Estimated total cost")
