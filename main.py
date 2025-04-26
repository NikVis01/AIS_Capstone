import modal
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
from typing import Callable
import os

### Testing URL: https://www.shopifyacademy.com/

# Import our modules
from modal_scraper import scrape_website
from infer import analyze_layout
from ui_analyzer import analyze_ui

# Create the Modal app
app = modal.App("visor")

# Creating volumes (Note to self: cache model in model-volume for later)
scraper_volume = modal.Volume.from_name("scraper-volume", create_if_missing=True)
model_volume = modal.Volume.from_name("model-volume", create_if_missing=True)

# Creating a base image for all functions, tried to seperate but it shit itself
# I know this looks like a crazy number of downloads but roll with it
base_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "pip",
        "libnss3",
        "libglib2.0-0",
        "libasound2",
        "libx11-6",
        "libgl1-mesa-glx",
        "tesseract-ocr",
        "libtesseract-dev"
    )
    .pip_install(
        "playwright==1.41.2",
        "beautifulsoup4",
        "transformers",
        "torch",
        "Pillow",
        "numpy",
        "scikit-learn",
        "huggingface_hub",
        "opencv-python-headless",
        "accelerate",
        "sentencepiece",
        "protobuf",
        "fastapi",
        "python-multipart",
        "uvicorn",
        "pydantic",
        "pytesseract"
    )
    .run_commands(
        "playwright install chromium",
        "playwright install-deps chromium"
    )
)

@app.function(
    image=base_image,
    volumes={"/scraper-volume": scraper_volume},
    timeout=3600,
    cpu=4,
    allow_concurrent_inputs=1000
)
def scrape(url):
    """Modal function to scrape a website."""
    return scrape_website(url, "/scraper-volume")  # This will save screenshot.png in /scraper-volume

@app.function(
    image=base_image,
    volumes={
        "/scraper-volume": scraper_volume,
        "/model-volume": model_volume
    },
    secrets=[modal.Secret.from_name("huggingface-secret")],
    gpu="H100",
    cpu=8,
    timeout=3600,
    memory=32768,
    allow_concurrent_inputs=1000
)
def analyze(image_path, hf_token=[modal.Secret.from_name("huggingface-secret")]):
    """Modal function to analyze a screenshot."""

    # The screenshot is directly in /scraper-volume/screenshot.png, no /data subfolder
    return analyze_layout("/scraper-volume/screenshot.png", hf_token)

@app.function(
    image=base_image,
    volumes={"/model-volume": model_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    gpu="H100",
    cpu=8,
    timeout=3600,
    memory=32768,
    allow_concurrent_inputs=1000
)
def get_ui_suggestions(predictions):
    """Modal function to get UI suggestions."""
    return analyze_ui(predictions)

@app.function(
    image=base_image,
    cpu=2,
    timeout=3600,
    allow_concurrent_inputs=1000
)
@modal.asgi_app()
def create_asgi() -> Callable:
    web_app = FastAPI()

    @web_app.get("/", response_class=HTMLResponse)
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VISOR</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
            
            <!-- GETTING A COOLER FONT -->
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Special+Gothic+Expanded+One&display=swap" rel="stylesheet">

            <script src="https://unpkg.com/htmx.org@1.9.10"></script>
            
        </head>
        <body style="background-color: Thistle;" class="text-blue-900">
            <div class="max-w-3xl mx-auto p-8">
                <h1 style="font-family: 'Special Gothic Expanded One', sans-serif;" class="text-9xl font-bold text-blue-900 flex items-center gap-4">
                    Visor
                </h1>

                <h2 class="text-xl font-bold mb-4 text-blue-900">Wild AI suggestions for UX design</h2>

                <form hx-post="/analyze" hx-target="#output" hx-indicator="#loading">
                    <input type="url" name="url" class="border border-blue-900 p-2 w-full rounded focus:outline-none focus:border-black" required placeholder="Enter website URL">
                    <button type="submit" class="bg-blue-900 text-white p-2 mt-2 w-full rounded hover:bg-blue-600 transition-colors">Analyze</button>
                </form>
                <div id="loading" class="htmx-indicator mt-4">
                    <div class="text-center">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue border-t-transparent"></div>
                        <p class="mt-2 text-blue-900">Checking out your website...</p>
                    </div>
                </div>
                <div id="output" class="mt-4"></div>
            </div>
        </body>
        </html>
        """

    @web_app.post("/analyze", response_class=HTMLResponse)
    async def analyze_url(url: str = Form(...)):
        """
        Shoutout cursor for frontend.
        """
        print("Starting analysis...")
        try:
            print(f"Processing URL: {url}")
            
            print("Starting scrape...")
            scrape_result = scrape.remote(url)
            print(f"Scrape result: {scrape_result}")
            if not scrape_result.get("success"):
                return """
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Failed to scrape website. Please check the URL and try again.
                </div>
                """
            
            print("Starting layout analysis...")
            analysis = analyze.remote(scrape_result["screenshot_path"])
            print(f"Analysis result: {analysis}")
            if not analysis.get("success"):
                return """
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Failed to analyze layout. Please try again.
                </div>
                """
            
            print("Getting UI suggestions...")
            suggestions = get_ui_suggestions.remote(analysis["predictions"])
            print(f"Suggestions result: {suggestions}")
            if not suggestions.get("success"):
                return """
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Failed to generate suggestions. Please try again.
                </div>
                """

            print("Formatting results...")
            elements_list = "".join([f"<li class='mb-1 text-blue-900'>{p}</li>" for p in analysis["predictions"]])
            return f"""
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-bold mb-4 text-blue-900">Analysis Results</h2>
                
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-2 text-blue-900">Detected UI Elements:</h3>
                    <ul class="list-disc pl-5 text-blue-900">{elements_list}</ul>
                </div>
                
                <div>
                    <h3 class="text-lg font-semibold mb-2 text-blue-900">Where to go from here:</h3>
                    <div class="bg-white p-4 rounded border border-blue-900">
                        <pre class="whitespace-pre-wrap text-blue-900">{suggestions["suggestions"]}</pre>
                    </div>
                </div>
            </div>
            """
        except Exception as e:
                print(f"Error during analysis: {str(e)}")
                import traceback
                traceback.print_exc()
                return f"""
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Error: {str(e)}
                </div>
                """

    return web_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:create_asgi", host="0.0.0.0", port=5000, reload=True) 