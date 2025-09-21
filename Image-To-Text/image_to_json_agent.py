#!/usr/bin/env python3
"""
Image to JSON Agent using Gemini Flash 1.5
Converts images to structured JSON format using Google's Gemini Flash 1.5 model.
"""

import os
import json
import base64
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ImageToJSONAgent:
    """Agent that converts images to JSON using Gemini Flash 1.5 model."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent with API key.
        
        Args:
            api_key: Google AI API key. If None, will try to get from environment variable.
        """
        if api_key is None:
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            if not api_key:
                raise ValueError(
                    "API key not provided. Set GOOGLE_AI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate that the file is a valid image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def convert_image_to_json(
        self, 
        image_path: str, 
        prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Convert image to JSON using Gemini Flash 1.5.
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for the conversion (optional)
            max_tokens: Maximum tokens for the response
            
        Returns:
            Dictionary containing the JSON response and metadata
        """
        # Validate image
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not self.validate_image(image_path):
            raise ValueError(f"Invalid image file: {image_path}")
        
        # Default prompt if none provided
        if prompt is None:
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
        
        try:
            # Load and process the image
            image = Image.open(image_path)
            
            # Generate content using Gemini
            response = self.model.generate_content([
                prompt,
                image
            ], generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.1
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
            
            return {
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
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "image_path": image_path,
                    "model": "gemini-1.5-flash"
                }
            }
    
    def save_json_output(self, result: Dict[str, Any], output_path: str) -> None:
        """
        Save the JSON result to a file.
        
        Args:
            result: The result dictionary from convert_image_to_json
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Convert images to JSON using Gemini Flash 1.5"
    )
    parser.add_argument(
        "image_path", 
        help="Path to the input image file"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output JSON file path (default: image_name.json)"
    )
    parser.add_argument(
        "-p", "--prompt", 
        help="Custom prompt for image analysis"
    )
    parser.add_argument(
        "--api-key", 
        help="Google AI API key (or set GOOGLE_AI_API_KEY env var)"
    )
    parser.add_argument(
        "--max-tokens", 
        type=int, 
        default=4096,
        help="Maximum tokens for response (default: 4096)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = ImageToJSONAgent(api_key=args.api_key)
        
        # Convert image to JSON
        print(f"Processing image: {args.image_path}")
        result = agent.convert_image_to_json(
            args.image_path, 
            prompt=args.prompt,
            max_tokens=args.max_tokens
        )
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            image_name = Path(args.image_path).stem
            output_path = f"{image_name}.json"
        
        # Save result
        agent.save_json_output(result, output_path)
        
        if result["success"]:
            print(f"✅ Successfully converted image to JSON!")
            print(f"📁 Output saved to: {output_path}")
            print(f"📊 Tokens used: {result['metadata']['tokens_used']}")
        else:
            print(f"❌ Error: {result['error']}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
