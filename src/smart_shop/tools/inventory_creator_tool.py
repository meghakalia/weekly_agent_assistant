"""
Inventory Creator Tool for SmartShop Crew

This tool reads the latest image_analysis_*.json file from the outputs directory
and creates a structured inventory JSON file.
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
from typing import Optional
from crewai.tools import BaseTool


class InventoryCreatorTool(BaseTool):
    """Tool to create inventory from image analysis data."""
    
    name: str = "inventory_creator"
    description: str = """
    Creates an inventory JSON file from the latest image_analysis_*.json file.
    Reads the most recent image analysis file from the outputs directory and 
    extracts items, quantities, prices, and date to create a structured inventory.
    """
    
    def _run(
        self, 
        output_dir: str = "./outputs",
        inventory_filename: Optional[str] = None
    ) -> str:
        """
        Create inventory from the latest image analysis file.
        
        Args:
            output_dir: Directory containing image analysis files
            inventory_filename: Optional custom filename for inventory
            
        Returns:
            JSON string with inventory data
        """
        try:
            # Find the latest image_analysis_*.json file
            pattern = os.path.join(output_dir, "image_analysis_*.json")
            image_files = glob.glob(pattern)
            
            if not image_files:
                return json.dumps({
                    "success": False,
                    "error": f"No image_analysis_*.json files found in {output_dir}"
                }, indent=2)
            
            # Get the most recent file
            latest_file = max(image_files, key=os.path.getctime)
            
            # Read the image analysis data
            with open(latest_file, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
            
            if not image_data.get("success", False):
                return json.dumps({
                    "success": False,
                    "error": "Image analysis data indicates failure"
                }, indent=2)
            
            # Extract items from the image analysis
            # Handle nested json_data structure
            json_data = image_data.get("json_data", {})

            # Check if there's a nested json_data (from tool output)
            if "json_data" in json_data:
                json_data = json_data.get("json_data", {})

            text_data = json_data.get("text", {})
            items_purchased = text_data.get("items_purchased", [])
            totals = text_data.get("totals", {})
            transaction_details = text_data.get("transaction_details", {})
            
            # Create inventory structure
            inventory = {
                "inventory": {
                    "date": transaction_details.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "items": [],
                    "total_items": len(items_purchased),
                    "total_value": totals.get("total", 0.0),
                    "subtotal": totals.get("subtotal", 0.0),
                    "tax": totals.get("tax", 0.0)
                }
            }
            
            # Process each item
            for item in items_purchased:
                inventory_item = {
                    "item": item.get("item", item.get("item_name", "Unknown Item")),
                    "quantity": item.get("quantity", 1),
                    "price": item.get("price", 0.0)
                }
                inventory["inventory"]["items"].append(inventory_item)
            
            # Generate inventory filename if not provided
            if not inventory_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                inventory_filename = f"inventory_{timestamp}.json"
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save inventory file
            inventory_path = os.path.join(output_dir, inventory_filename)
            with open(inventory_path, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
            
            # Return success result
            result = {
                "success": True,
                "inventory_data": inventory,
                "source_file": latest_file,
                "output_file": inventory_path,
                "items_count": len(items_purchased),
                "total_value": totals.get("total", 0.0)
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "output_dir": output_dir
            }
            return json.dumps(error_result, indent=2)
