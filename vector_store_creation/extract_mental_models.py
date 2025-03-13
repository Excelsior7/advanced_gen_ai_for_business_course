import requests
from bs4 import BeautifulSoup
import json

def extract_mental_models(url):
    """
    Extract mental models from a given URL.
    
    Args:
        url (str): The URL to extract mental models from
        
    Returns:
        list: A list of dictionaries containing the mental models
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # Fetch the HTML content with headers
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
    except requests.RequestException as e:
        print(f"Error fetching the content: {e}")
        return []
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize the list to store the mental models
    mental_models = []
    
    # Find all paragraphs that might contain mental models
    paragraphs = soup.find_all('p')
    
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        # Check if this paragraph contains a mental model title (has a <strong> tag)
        strong_tag = p.find('strong')
        if strong_tag:
            # Extract the title and text
            title = strong_tag.get_text().strip()
            
            # The mental model text is the rest of the paragraph after removing the strong tag
            # First, let's get the full text of the paragraph
            full_text = p.get_text().strip()
            
            # Remove the title from the full text to get just the mental model text
            mental_model_text = full_text[len(title):].strip()
            
            # Check if the next paragraph contains the primary source
            source = None
            if i + 1 < len(paragraphs) and paragraphs[i + 1].find('em'):
                source = paragraphs[i + 1].get_text().strip()
                i += 1  # Skip the source paragraph in the next iteration
            
            # Add the mental model to our list
            mental_models.append({
                'title': title,
                'mental_model': mental_model_text,
                'source': source
            })
        
        i += 1
    
    return mental_models

def save_to_json(mental_models, output_file):
    """
    Save the mental models to a JSON file.
    
    Args:
        mental_models (list): The list of mental models
        output_file (str): The path to the output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mental_models, f, ensure_ascii=False, indent=4)


url = "https://junto.investments/mental-models/"

mental_models = extract_mental_models(url)

print(f"Extracted {len(mental_models)} mental models")

save_to_json(mental_models, "mental_models.json")

if mental_models:
    print("\nSample mental model:")
    print(f"Title: {mental_models[0]['title']}")
    print(f"Mental Model: {mental_models[0]['mental_model'][:100]}...")
    print(f"Source: {mental_models[0]['source']}")