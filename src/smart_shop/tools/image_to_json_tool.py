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
        "Converts images to structured JSON format using Google's Gemini Flash 1.5 model. "
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
            self._model = genai.GenerativeModel('gemini-1.5-flash')
        
        return self._model

    def _run(self, image_path: str, custom_prompt: Optional[str] = None, output_path: Optional[str] = None) -> str:
        """
        Convert image to JSON using Gemini Flash 1.5.
        
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
                Analyze this image and convert it to a structured JSON format. 
                Include the following information:
                - A description of what you see in the image
                - Any text that appears in the image (OCR)
                - Objects, people, or items visible
                - Colors, shapes, and visual elements
                - Any other relevant details that can be extracted
                
                Return the response as a valid JSON object with clear structure.
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
                    "model": "gemini-1.5-flash",
                    "tokens_used": len(response_text.split()),
                    "raw_response": response_text
                }
            }
            
            # Save to file if output_path is provided
            if output_path:
                try:
                    # Use configured output directory if path is relative
                    if not os.path.isabs(output_path):
                        output_path = os.path.join(config['output_dir'], output_path)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    result["output_file"] = output_path
                except Exception as e:
                    result["save_error"] = str(e)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "metadata": {
                    "image_path": image_path,
                    "model": "gemini-1.5-flash"
                }
            }
            return json.dumps(error_result, indent=2)
