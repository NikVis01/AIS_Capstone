
# KTH AI Society Fullstack AI course capstone project: Visor AI

![image](https://github.com/user-attachments/assets/d138848d-3475-41aa-8d51-08bbf1fe521d)

By: Niklavs Visockis

## v1 of UI reading and analysis app 
Core idea is that you input a link and it returns a list of ideas/design principles that you should keep in mind while developing and refining
Design theory and UI ideas come largly from various online sources for UI design trends and guides for making intuitive and friendly UX

Some theory used to back up prompting choices:

https://www.appcues.com/blog/user-onboarding-starts-with-a-good-landing-page

https://www.framer.com/blog/web-design-trends/

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
- Deploy modal main
- Copy link that ends with "...modal.run" in browser
- Input a link of your choice and wait for containers to spin up
- WARNING: The web app is implemented as a sync fasthtml app for sake of simplicity, it may take a while to run

### Limitations
- I could have used GPT-4o for this since it can read UI from a link and give suggestions straight up. However; this is lame and boring. I learned more doing it this way. It works decently. 
- Business use-case is slim if not non-existent for the current application. 
- Bipassing Captcha is not implemented

The base code can be fine tuned for a wide scope of different applications such as:
1. Landing page analysis and suggestions to onboard clients easier for Saas
2. A/B testing of sign-in or checkout pages
3. Instead of UI it could read legal documents, shipping offers, contracts, etc...
4. Advertisment screening and marketing media suggestions (posters, blog formatting, email list content)
5. Competitor comparison and feature updates; keep track of your competion and new features they add with scheduled runs of this app
