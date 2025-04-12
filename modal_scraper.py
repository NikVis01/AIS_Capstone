from typing import Dict, List, Any, Union
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def extract_html_data(html_content) -> Dict[str, Any]:
    """Extract raw HTML data without any analysis."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    elements = {
        "headings": [{"tag": str(h.name), "text": str(h.get_text(strip=True))} for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
        "buttons": [{"text": str(btn.get_text(strip=True))} for btn in soup.find_all('button')],
        "inputs": [{"type": str(inp.get('type', 'text'))} for inp in soup.find_all('input')],
        "links": [{"text": str(link.get_text(strip=True)), "href": str(link.get('href', ''))} for link in soup.find_all('a')]
    }
    
    return {
        "title": str(soup.title.string) if soup.title else "",
        "elements": elements
    }

def scrape_website(url: str, output_dir: str) -> Dict[str, Any]:
    """Scrape a single website and save screenshot + metadata."""
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"Scraping URL: {url}")
            page.goto(url, wait_until="networkidle")
            
            # Get page dimensions
            page_height = page.evaluate("document.documentElement.scrollHeight")
            page_width = page.evaluate("document.documentElement.scrollWidth")
            
            # Set viewport to full page size
            page.set_viewport_size({"width": page_width, "height": page_height})
            
            # Take full-page screenshot
            screenshot_path = os.path.join(output_dir, "screenshot.png")
            page.screenshot(
                path=screenshot_path,
                full_page=True
            )
            
            html_content = page.content()
            
            # Extract data
            data = {
                "url": str(url),
                "timestamp": str(datetime.now().strftime('%Y%m%d_%H%M%S')),
                "screenshot": {
                    "path": screenshot_path,
                    "width": page_width,
                    "height": page_height
                },
                "html_data": extract_html_data(html_content)
            }
            
            # Save metadata
            json_path = os.path.join(output_dir, "metadata.json")
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print("✓ Scraping successful")
            return {
                "success": True,
                "screenshot_path": screenshot_path,
                "json_path": json_path,
                "metadata": data
            }
            
        except Exception as e:
            print(f"✗ Failed to scrape: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
        
        finally:
            browser.close() 