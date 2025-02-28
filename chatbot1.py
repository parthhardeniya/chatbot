import spacy
import requests
from bs4 import BeautifulSoup

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Documentation URLs
DOCUMENTATION_URLS = {
    "segment": "https://segment.com/docs/?ref=nav",
    "mparticle": "https://docs.mparticle.com/",
    "lytics": "https://docs.lytics.com/",
    "zeotap": "https://docs.zeotap.com/home/en-us/"
}

# Process user queries
def process_query(query):
    doc = nlp(query)
    intent = None
    platform = None
    
    for token in doc:
        if token.text.lower() in ["how", "steps", "guide", "setup", "create", "build", "integrate"]:
            intent = "how-to"
        if token.text.lower() in ["segment", "mparticle", "lytics", "zeotap"]:
            platform = token.text.lower()
    
    return intent, platform

# Scrape documentation
def scrape_docs(platform, query):
    url = DOCUMENTATION_URLS.get(platform)
    if not url:
        return "Platform documentation not found."
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return f"Error fetching documentation: Status Code {response.status_code}"
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        keywords = query.lower().split()
        relevant_sections = []
        
        for tag in soup.find_all(["h1", "h2", "h3", "p"]):
            if any(word in tag.text.lower() for word in keywords):
                parent_section = tag.find_previous(["h1", "h2"])
                relevant_sections.append((parent_section.text.strip() if parent_section else "Unknown Section") + "\n" + tag.text.strip())
        
        if not relevant_sections:
            return f"No relevant information found in {platform.capitalize()} documentation."
        
        return "\n\n".join(relevant_sections[:3])  # Return top 3 sections

    except Exception as e:
        return f"Error fetching documentation: {e}"

# Generate chatbot response
def generate_response(intent, platform, extracted_info):
    if intent == "how-to":
        return f"Here’s how to do that in {platform.capitalize()}:\n\n{extracted_info}"
    else:
        return "I can only help with how-to questions related to Segment, mParticle, Lytics, and Zeotap."

# Check if the question is relevant
def is_relevant(query):
    relevant_keywords = ["segment", "mparticle", "lytics", "zeotap", "source", "profile", "audience", "integrate"]
    return any(keyword in query.lower() for keyword in relevant_keywords)

# Main chatbot function
def chatbot(query):
    if not is_relevant(query):
        return "Sorry, I can only answer questions related to Segment, mParticle, Lytics, and Zeotap."
    
    intent, platform = process_query(query)
    if not platform:
        return "Please specify a platform: Segment, mParticle, Lytics, or Zeotap."
    
    extracted_info = scrape_docs(platform, query)
    return generate_response(intent, platform, extracted_info)

# Run chatbot
if __name__ == "__main__":
    print("Welcome to the CDP How-To Chatbot! Ask me anything about Segment, mParticle, Lytics, or Zeotap.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        
        response = chatbot(user_input)
        print(f"Chatbot: {response}")
