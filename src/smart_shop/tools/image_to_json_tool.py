from crewai.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json
import base64
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


class ImageToJSONToolInput(BaseModel):
    """Input schema for ImageToJSONTool."""
    image_path: str = Field(..., description="Path to the image file to convert to JSON")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for image analysis (optional)")
    output_path: Optional[str] = Field(None, description="Output path for the JSON file (optional)")


class ImageToJSONTool(BaseTool):
    name: str = "image_to_json_converter"
    description: str = (
        "Converts images to structured JSON format using Google's Gemini 2.5 Flash model. "
        "Analyzes images and extracts text, objects, colors, and other visual elements into a structured JSON format. "
        "Useful for processing receipts, documents, photos, and any visual content that needs to be converted to structured data."
    )
    args_schema: Type[BaseModel] = ImageToJSONToolInput

    def __init__(self):
        super().__init__()
        # Initialize model lazily to avoid issues during crew initialization
        self._model = None
        self._config = None

    def _get_config(self):
        """Get or initialize configuration from environment."""
        if self._config is None:
            self._config = {
                'max_tokens': int(os.getenv('MAX_TOKENS', '4096')),
                'temperature': float(os.getenv('TEMPERATURE', '0.1')),
                'output_dir': os.getenv('OUTPUT_DIR', './outputs')
            }
            # Create output directory if it doesn't exist
            os.makedirs(self._config['output_dir'], exist_ok=True)
        return self._config

    def _get_model(self):
        """Get or initialize the Gemini model."""
        if self._model is None:
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            if not api_key or api_key == 'your_google_ai_api_key_here':
                raise ValueError(
                    "GOOGLE_AI_API_KEY environment variable not set or invalid. "
                    "Please set it in your .env file or environment. "
                    "See env_template.txt for reference."
                )
            
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-2.5-flash')
        
        return self._model

    def _generate_unique_filename(self, base_path: str) -> str:
        """Generate a unique filename to avoid overwriting existing files."""
        path = Path(base_path)
        
        # If file doesn't exist, return original path
        if not path.exists():
            return base_path
        
        # Extract components
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create unique filename
        unique_filename = f"{stem}_{timestamp}{suffix}"
        unique_path = parent / unique_filename
        
        # If still exists (very unlikely), add counter
        counter = 1
        while unique_path.exists():
            unique_filename = f"{stem}_{timestamp}_{counter}{suffix}"
            unique_path = parent / unique_filename
            counter += 1
        
        return str(unique_path)

    def _run(self, image_path: str, custom_prompt: Optional[str] = None, output_path: Optional[str] = None) -> str:
        """
        Convert image to JSON using Gemini 2.5 Flash.

        Args:
            image_path: Path to the image file
            custom_prompt: Custom prompt for the conversion (optional)
            output_path: Output path for the JSON file (optional)

        Returns:
            String containing the result of the conversion
        """
        try:
            # Validate image path
            if not os.path.exists(image_path):
                return f"Error: Image file not found at {image_path}"
            
            # Validate image file
            try:
                with Image.open(image_path) as img:
                    img.verify()
            except Exception as e:
                return f"Error: Invalid image file - {str(e)}"
            
            # Default prompt if none provided
            if custom_prompt is None:
                prompt = """
                Analyze this image and convert it to a structured JSON format following this EXACT structure:
                
                {
                  "image_description": "Brief description of what you see in the image",
                  "text": {
                    "store_information": "Store name, address, phone if visible",
                    "member_information": "Member details if visible",
                    "items_purchased": [
                      {"item": "Item name", "quantity": 1, "price": 0.00},
                      {"item": "Item name", "quantity": 1, "price": 0.00}
                    ],
                    "totals": {
                      "subtotal": 0.00,
                      "tax": 0.00,
                      "total": 0.00
                    },
                    "payment_information": {
                      "aid": "Payment aid if visible",
                      "seq": "Sequence number if visible",
                      "app": "App number if visible",
                      "tran_id": "Transaction ID if visible",
                      "merchant_id": "Merchant ID if visible"
                    },
                    "transaction_details": {
                      "date": "Date if visible",
                      "time": "Time if visible",
                      "store_number": "Store number if visible",
                      "terminal_number": "Terminal number if visible",
                      "transaction_number": "Transaction number if visible",
                      "operator_number": "Operator number if visible",
                      "customer_name": "Customer name if visible",
                      "total_items_sold": "Number of items if visible",
                      "instant_savings": "Savings amount if visible"
                    }
                  },
                  "objects": ["List of objects visible in the image"],
                  "people": ["List of people visible in the image"],
                  "colors": ["List of dominant colors in the image"],
                  "shapes": ["List of shapes visible in the image"],
                  "visual_elements": ["List of visual elements like text, barcode, etc."],
                  "other_details": {
                    "date_of_purchase": "Date if visible",
                    "time_of_purchase": "Time if visible",
                    "payment_type": "Payment type if visible",
                    "total_items": "Total number of items if visible"
                  }
                }
                
                IMPORTANT: Follow this EXACT structure. Do not deviate from this format.
                If information is not available, use appropriate default values or empty strings.
                """
            else:
                prompt = custom_prompt
            
            # Load and process the image
            image = Image.open(image_path)
            
            # Get the model and config (initializes if needed)
            model = self._get_model()
            config = self._get_config()
            
            # Generate content using Gemini with environment-configured settings
            response = model.generate_content([
                prompt,
                image
            ], generation_config=genai.types.GenerationConfig(
                max_output_tokens=config['max_tokens'],
                temperature=config['temperature']
            ))
            
            # Parse the response
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed_json = json.loads(json_str)
                else:
                    # If no JSON found, wrap the response in a JSON structure
                    parsed_json = {
                        "description": response_text,
                        "raw_response": response_text
                    }
                
            except json.JSONDecodeError:
                # If JSON parsing fails, wrap in a structure
                parsed_json = {
                    "description": response_text,
                    "raw_response": response_text,
                    "parse_error": "Response could not be parsed as JSON"
                }
            
            # Create result structure
            result = {
                "success": True,
                "json_data": parsed_json,
                "metadata": {
                    "image_path": image_path,
                    "image_size": image.size,
                    "model": "gemini-2.5-flash",
                    "tokens_used": len(response_text.split()),
                    "raw_response": response_text
                }
            }
            
            # Save to file - generate unique filename if output_path is not provided
            if not output_path:
                # Generate a unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"image_analysis_{timestamp}.json"
            
            try:
                # Use configured output directory if path is relative
                if not os.path.isabs(output_path):
                    output_path = os.path.join(config['output_dir'], output_path)
                
                # Generate unique filename to avoid overwriting
                unique_output_path = self._generate_unique_filename(output_path)
                
                with open(unique_output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                result["output_file"] = unique_output_path
                result["original_path"] = output_path
                result["unique_filename"] = True
            except Exception as e:
                result["save_error"] = str(e)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "metadata": {
                    "image_path": image_path,
                    "model": "gemini-2.5-flash"
                }
            }
            return json.dumps(error_result, indent=2)
