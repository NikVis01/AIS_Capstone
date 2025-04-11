from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Dict, Any, List

### Link to model used: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 

def analyze_ui(predictions: list) -> dict:
    """Generate UI suggestions based on detected elements using Mistral-7B-Instruct."""
    try:
        ### Wondering if i shouldn't remove duplicate elements/readings from predictions.
        ### Keeping them for now so that the model can see if the page is cluttered.
        
        # Loading model and creating pipeline
        model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        llm = pipeline("text-generation", model=model, tokenizer=tokenizer, use_fast=True)
        
        # Create prompt with detected elements
        elements_str = ", ".join(predictions)
        prompt = f"""<s>[INST] You are a UX expert. Based on these UI elements: {elements_str}, provide specific improvement suggestions. Focus on:
1. Specific features on the website (e.g. chatbot, search bar, signup page, payment plans, contact info for customer service and more)
2. User experience enhancements (e.g., better navigation or interaction)
3. Cluttering of elements (too many elements on the page is really bad)
4. Visual hierarchy (Is the site readable?)
5. links to other pages (extensive docs for how to use the service is positive)
6. Links to tutorials or courses (this is good for the user)

Keep suggestions concise and actionable. Please return a list of max 10 improvements [/INST]"""
        
        # Generating the suggestions!!!
        output = llm(
            prompt,
            max_new_tokens=200,
            do_sample=False,
            temperature=0.7
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