// UI Elements
const urlInput = document.getElementById('urlInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('results');
const loadingSection = document.getElementById('loading');
const analysisResults = document.getElementById('analysisResults');
const elementsList = document.getElementById('elementsList');
const suggestionsList = document.getElementById('suggestionsList');

// Event Listeners
analyzeBtn.addEventListener('click', analyzeWebsite);

async function analyzeWebsite() {
    const url = urlInput.value.trim();
    if (!url) return;

    // Show loading state
    analyzeBtn.disabled = true;
    resultsSection.style.display = 'block';
    loadingSection.style.display = 'flex';
    analysisResults.style.display = 'none';

    try {
        // Call FastAPI endpoint to analyze the website
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    } finally {
        analyzeBtn.disabled = false;
        loadingSection.style.display = 'none';
    }
}

function displayResults(data) {
    // Clear previous results
    elementsList.innerHTML = '';
    suggestionsList.innerHTML = '';

    // Display detected elements
    if (data.predictions && data.predictions.length > 0) {
        data.predictions.forEach(element => {
            const li = document.createElement('li');
            li.textContent = element;
            elementsList.appendChild(li);
        });
    }

    // Display suggestions
    if (data.analysis && data.analysis.suggestions) {
        const suggestions = data.analysis.suggestions.split('\n');
        suggestions.forEach(suggestion => {
            if (suggestion.trim()) {
                const p = document.createElement('p');
                p.textContent = suggestion.trim();
                suggestionsList.appendChild(p);
            }
        });
    }

    // Show results
    analysisResults.style.display = 'block';
}

function showError(message) {
    // Clear previous results
    elementsList.innerHTML = '';
    suggestionsList.innerHTML = '';

    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    suggestionsList.appendChild(errorDiv);

    // Show results section
    analysisResults.style.display = 'block';
}

// Add some basic validation
urlInput.addEventListener('input', () => {
    const url = urlInput.value.trim();
    analyzeBtn.disabled = !url;
}); 