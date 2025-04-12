from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Dict, Any, List
import os

### Link to model used: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 

def analyze_ui(predictions: list) -> dict:
    """Generate UI suggestions based on detected elements using Mistral-7B-Instruct."""
    try:
        ### Wondering if i shouldn't remove duplicate elements/readings from predictions.
        ### Keeping them for now so that the model can see if the page is cluttered.
        
        # Loading model and creating pipeline
        model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        
        # Check if model is cached in model_volume
        model_path = "/model-volume/mistral-7b-instruct-v0.3"
        if os.path.exists(model_path):
            print("Loading cached Mistral model...")
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype="auto",
                device_map="auto"
            )
        else:
            print("Downloading and caching Mistral model...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            # Cache the model
            model.save_pretrained(model_path)
            tokenizer.save_pretrained(model_path)
        
        llm = pipeline("text-generation", model=model, tokenizer=tokenizer, use_fast=True)
        
        # Create prompt with detected elements

        elements_str = ", ".join(predictions)
        prompt = f"""<s>[INST] You are a UX expert for UI comprehension and readability. You are given the following description of the UI: f{elements_str}.
        From this description return a list of suggestions for the page design specifically connecting to features in the description.
        Certain UI features will be better or worse than others, make sure to include this perspective.
        Give insights based off of the context of the website and depending on its function. 
        [/INST]
        """ # Added last row just now
        
        print(elements_str) # For debugging and such

        # Generating the suggestions!!!
        output = llm(
            prompt,
            max_new_tokens=400,
            do_sample=True,
            temperature=1.5 # Was 0.8 and worked pretty well but was predictable & boring
        )
        suggestions = output[0]["generated_text"].split("[/INST]")[1].strip()
        
        return {
            "success": True,
            "suggestions": suggestions,
            "detected_elements": list(predictions)  # Return all elements, including duplicates
        }
        
    except Exception as e:
        print(f"UI Analysis Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 