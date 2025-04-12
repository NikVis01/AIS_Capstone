import re
from transformers import AutoProcessor, LlavaForConditionalGeneration
from PIL import Image
import torch
from typing import Dict, Any
import os

### Link to model used: https://huggingface.co/llava-hf/llava-1.5-7b-hf

def analyze_layout(image_path, hf_token):
    """Analyzing UI screenshot with LLaVA 1.5."""
    try:
        # Load LLaVA model and processor
        model_id = "llava-hf/llava-1.5-7b-hf"
        
        # Check if model is cached in model_volume
        model_path = "/model-volume/llava-1.5-7b-hf"
        if os.path.exists(model_path):
            print("Loading cached model...")
            model = LlavaForConditionalGeneration.from_pretrained(
                model_path,
                token=hf_token,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            ).to(0)
            processor = AutoProcessor.from_pretrained(model_path, token=hf_token)
        else:
            print("Downloading and caching model...")
            model = LlavaForConditionalGeneration.from_pretrained(
                model_id,
                token=hf_token,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            ).to(0)
            processor = AutoProcessor.from_pretrained(model_id, token=hf_token, use_fast=True)
            
            # Cache the model
            model.save_pretrained(model_path)
            processor.save_pretrained(model_path)
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Define chat conversation with image
        prompt = "List all the features you can see in this UI image. Format as numbered list. " \
        "Focus on functional and interactive elements such as navigation, signup forms, course links, guides, offerings, pricing, etc. " \
        "Make note of which colors are primarily used in the site (e.g if the site has vibrant and contrasting color schemes or not)" \
        "Be explicit about what kind of service the website provides (e.g ecommerce, video game, SaaS, startup, design store, etc )" # Changed this right now

        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
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
            max_new_tokens=200, ### Play around with this shit for best results
            do_sample=False ### Tried this as true it was pretty cool but lwk mistral shit itself a lil
        )
        
        # Decode the response, skipping the prompt tokens
        description = processor.decode(output[0][2:], skip_special_tokens=True, use_fast=True)
        print(description)
        # Debug logging
        # print(f"Raw description: {description}")
        
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
