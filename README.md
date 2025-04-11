
# KTH AI Society Fullstack AI course capstone project!!!
By: Niklavs Visockis

## v1 of UI reading and analysis app 

### Model Architecture: 
- LLaVA-1.5 used for image-to-text returns list of detected UI elements from a screenshot
- Mistral-7b takes list of UI elements and returns a list of suggestions for improvements

### Code Structure:
- Modal used for web deployment of web-scraper, LLaVa and Mistral-7b 
- modal_scraper.py contains web scraper that takes full length screenshot of the page as well as HTML data (for training, currently not used)
- infer.py contains the LLaVA model and shows as "analyze" function in modal
- ui_analyzer.py contains the LLM and shows as "suggestions" function in modal
- main.py creates base image and modal app importing the previously mentioned models from their respective files

### How to run:
- deploy modal main
- copy link that ends with "...modal.run" in browser
- Input a link of your choice and wait for containers to spin up
- WARNING: The web app is implemented as a sync fasthtml app for sake of simplicity, it may take a while

IF YOUR NAME HAPPENS TO BE TIMOTHY LINDBLOM:
- Im keeping the containers warm for you so just follow the following link and it should work fine: https://nikvis01--ui-analyzer-create-asgi.modal.run 

### Limitations and recognitions
- I could have used GPT-4o for this since it can read UI from a link and give suggestions straight up
- However; this is lame and boring. I learned more doing it this way. It works. 
- Business use-case is slim if not non-existent. The base code can be fine tuned for an array of different applications such as:
1. Landing page analysis and suggestions to onboard clients easier for Saas
2. A/B testing of sign-in or checkout pages
3. Instead of UI it could read legal documents, shipping offers, contracts, etc...
4. And many more applications!