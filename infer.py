from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from typing import Dict, Any

def analyze_layout(image_path: str) -> Dict[str, Any]:
    """Analyze a UI screenshot using BLIP model."""
    try:
        # Load BLIP model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Load and process image
        image = Image.open(image_path).convert("RGB")
        
        # Process image without conditional prompt for natural description
        inputs = processor(image, return_tensors="pt")
        out = model.generate(
            **inputs,
            max_length=100,  # Limiting length to get focused description
            num_beams=5,     # Beam search for better quality
            temperature=0.7   # Some creativity but not too wild
        )
        description = processor.decode(out[0], skip_special_tokens=True)
        
        # Debug logging
        print(f"Raw description: {description}")
        
        # Simple cleaning and splitting
        elements = [elem.strip() for elem in description.lower().split(".")]
        elements = [e for e in elements if e]  # Remove empty strings
        
        # Limit to 10 elements if we have more
        elements = elements[:10]
        
        # Debug logging
        print(f"Processed elements: {elements}")
        
        return {
            "success": True,
            "description": description,
            "predictions": elements
        }
        
    except Exception as e:
        print(f"Error in analyze_layout: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
