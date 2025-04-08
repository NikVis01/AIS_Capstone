import re
from transformers import AutoProcessor, LlavaForConditionalGeneration
from PIL import Image
import torch
from typing import Dict, Any

def analyze_layout(image_path, hf_token):
    """Analyzing UI screenshot with LLaVA 1.5."""
    try:
        # Load LLaVA model and processor
        model_id = "llava-hf/llava-1.5-7b-hf"
        model = LlavaForConditionalGeneration.from_pretrained(
            model_id,
            token=hf_token,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        ).to(0)
        
        processor = AutoProcessor.from_pretrained(model_id, token=hf_token)
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Define chat conversation with image
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "List all UI elements you can see in this interface. Focus on interactive elements, navigation, forms, and key features."},
                    {"type": "image", "image": image}
                ]
            }
        ]
        
        # Apply chat template
        prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
        
        # Process inputs
        inputs = processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        ).to(0, torch.float16)
        
        # Generate response
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False
        )
        
        # Decode the response, skipping the prompt tokens
        description = processor.decode(output[0][2:], skip_special_tokens=True, use_fast=True)
        
        # Debug logging
        print(f"Raw description: {description}")
        
        # Split into lines and clean up
        lines = description.strip().split('\n')
        # Keep only numbered lines and clean them up
        elements = []
        for line in lines:
            # Match lines that start with a number and period (e.g., "1.", "2.", etc.)
            if re.match(r'^\d+\.', line.strip()):
                # Remove the number and period, then strip whitespace
                cleaned = re.sub(r'^\d+\.\s*', '', line.strip())
                if cleaned:
                    elements.append(cleaned)
        
        return {
            "success": True,
            "description": description,  # Keep raw description for debugging
            "predictions": elements  # Send cleaned numbered list to Mistral
        }
        
    except Exception as e:
        print(f"Error in analyze_layout: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
