import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import openai
import pandas as pd
import requests
import time
import os

api_key = os.getenv("CHATGPT_KEY")
if not api_key:
    raise ValueError("Environment variable CHATGPT_KEY is not set.")
# Define scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Path to your credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name("D:\\BookNest\\utilities\\credentials.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet by URL or title
#sheet_url = "https://docs.google.com/spreadsheets/d/1WBAOPiIMEUuE0g30PUjHisoFlNpEDsdRmUjlPmkDnvI"
sheet_url = "https://docs.google.com/spreadsheets/d/182AATzul9y2SvvPAJlmZQHkDHotYGzY37njtcE73rUw"

sheet = client.open_by_url(sheet_url)

# Select worksheet by name or index
worksheet = sheet.get_worksheet(0)  # or use .worksheet("Sheet1")

# Read all data as a list of lists
data = worksheet.get_all_values()

# Print the data
#for row in data:
#    print("================================\n")
    #print(row)
 
# Get all rows as list of dicts (header must be present)
records = worksheet.get_all_records()

# Create JSON array from 'Title (English)' and 'Language' columns
json_array = []
cnt = 1
key_sn = "S_No"
key_title = "Book_Title"
key_author = "Author"
key_rent = "Rent_per_week"
key_language = "Language"

def get_google_books_data(title, author):
    query = f"{title} {author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url).json()
    if "items" in response:
        book_info = response["items"][0]["volumeInfo"]
        return {
            "description": book_info.get("description", ""),
            "categories": ", ".join(book_info.get("categories", []))
        }
    return {"description": "", "categories": ""}


def get_chatgpt_genres_and_age(title, author, description, categories):
    prompt = f"""
    Analyze the following book and provide:
    1. 3-5 detailed genres (comma-separated)
    2. The target age category. Choose ONLY from:
       - Toddler (0–4 years)
       - Children (5–12 years)
       - Teenage (13–17 years)
       - Young Adult (18–25 years)
       - Adult (26+ years)
       - All Ages

    Book details:
    Title: {title}
    Author: {author}
    Categories: {categories}
    Description: {description}

    Format your answer as:
    Genres: <comma separated list>
    Age Category: <exact label from the list above>
    """
    
    client = openai.OpenAI(
        api_key=api_key
    )
    response = client.chat.completions.create(
        model="gpt-4o",  # Note: changed from gpt-4o-mini to gpt-4
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


# Modify the main loop
for row in records:
    if row.get("Title (English)") and row["Author/Publisher"]:
        title = row["Title (English)"]
        author = row["Author/Publisher"]
        print(f"\nProcessing: {title} by {author}")
        
        # Get Google Books data
        try:
            google_data = get_google_books_data(title, author)
            description = google_data["description"]
            categories = google_data["categories"]
            
            if description or categories:
                print("Found Google Books data:")
                print(f"Categories: {categories}")
                print(f"Description length: {len(description)} chars")
                
                # Get enhanced categories from ChatGPT
                try:
                    print("Getting ChatGPT analysis...")
                    chatgpt_analysis = get_chatgpt_genres_and_age(title, author, description, categories)
                    print("\nChatGPT Analysis:")
                    print(chatgpt_analysis)
                    
                    # Add a small delay to respect API limits
                    time.sleep(1)
                except Exception as e:
                    print(f"ChatGPT API error: {str(e)}")
            else:
                print("No Google Books data found")
        except Exception as e:
            print(f"Google Books API error: {str(e)}")
        
        print("-" * 50)
        break
        
        
        