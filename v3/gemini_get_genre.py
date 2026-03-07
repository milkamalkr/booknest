import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from google import genai
import pandas as pd
import requests
import time
import os

# Use environment variable for API key
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise ValueError("Environment variable GEMINI_KEY is not set.")

gemini_client = genai.Client(api_key="AIzaSyB9wgZzpxY_4Imak8rwWLasi1o7By541mU")

#genai.configure(api_key=api_key)

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
#sheet_url = "https://docs.google.com/spreadsheets/d/1kzDWwU-PUyd_gLgh8irkXmNg3CEUp990UhEQbXfPfK0"
sheet_url = "https://docs.google.com/spreadsheets/d/17272qHOT8B95IVSj-VIZPn7YD1k5a4BYmptAvGZmM6w"
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
print("start")
API_KEY = "AIzaSyDKmKVCFSpKi6-ZOda-hCJNlPBvrGF-pZI"  # Paste your key here

def get_google_books_data(title, author):
    """
    Fetch book data from Google Books API with retry strategies and exponential backoff.
    Uses proper URL encoding and multiple search approaches with rate-limit handling.
    """
    queries = [
        f'"{title}" author:"{author}"',
        f'"{title}" {author}',
        f'{title} {author}',
        title,
    ]
    
    for query in queries:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                params = {'q': query, 'maxResults': 1, 'key': API_KEY}  # Add key here
                response = requests.get(
                    "https://www.googleapis.com/books/v1/volumes",
                    params=params,
                    timeout=5
                )
                
                # Handle rate limiting (429) with exponential backoff
                if response.status_code == 429:
                    wait_time = (2 ** attempt) + 1  # 2, 5, 10 seconds
                    print(f"  ⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if "items" in data and len(data["items"]) > 0:
                    book_info = data["items"][0].get("volumeInfo", {})
                    print(f"  ✓ Found via query: {query}")
                    return {
                        "description": book_info.get("description", ""),
                        "categories": ", ".join(book_info.get("categories", []))
                    }
                else:
                    break  # No results for this query, try next one
                    
            except requests.exceptions.Timeout:
                print(f"  ⏱ Timeout on query '{query}' (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
            except Exception as e:
                print(f"  Query failed ({query}): {str(e)}")
                break
    
    print(f"  ✗ No results for '{title}' by '{author}'")
    return {"description": "", "categories": ""}

# # Use Gemini model
# # Try latest model first, fallback to gemini-pro if not available
# try:
#     #model = genai.GenerativeModel("gemini-1.5-flash")  # Latest, fastest, cheapest
#     model = genai.GenerativeModel("gemini-pro")
# except Exception:
#     model = genai.GenerativeModel("gemini-pro")  # Fallback

def get_gemini_genres_and_age(title, author, description, categories):
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
   
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

#result = get_google_books_data("Harry Potter and the Prisoner of Azkaban", "J.K. Rowling")
#print(result)
with open("classified_genres.json", "r", encoding="utf-8") as f:
    classified_json = json.load(f)
    
# Modify the main loop
for idx, row in enumerate(records):
    # Skip rows till 5
    if idx <= 823:
        continue
    print("process - ", idx)
    if row.get("Title (English)") and row.get("Author/Publisher"):
        title = row["Title (English)"]
        author = row["Author/Publisher"]
        print(f"\nProcessing: {title} by {author}")

        # Get Google Books data
        try:
            google_data = get_google_books_data(title, author)

            # Use the description from the sheet if it is not empty
            if row.get("Description"):
                description = row["Description"]
            else:
                description = google_data["description"]

            categories = google_data["categories"]

            if description or categories:
                print("Found Google Books data:")
                print(f"Categories: {categories}")
                print(f"Description length: {len(description)} chars")

                # Get enhanced genres and age category from Gemini
                try:
                    print("Getting Gemini analysis...")
                    gemini_response = get_gemini_genres_and_age(title, author, description, categories)
                    print("\nGemini Response:")
                    print(gemini_response)

                    # Extract genres and age category from Gemini response
                    genres = ""
                    age_category = ""
                    for line in gemini_response.splitlines():
                        if line.startswith("Genres:"):
                            genres = line.replace("Genres:", "").strip()
                        elif line.startswith("Age Category:"):
                            age_category = line.replace("Age Category:", "").strip()

                    # Update the row object
                    
                    row["Description"] = description
                    from classify_genre import classify_genre
                    # Use classify_genre to determine main category for each genre
                    genre_list = [g.strip() for g in genres.split(",") if g.strip()]
                    main_categories = []
                    for g in genre_list:
                        main_cat = classify_genre(g, gemini_client, classified_json)
                        if main_cat not in main_categories:
                            main_categories.append(main_cat)
                        
                    row["MainCategory"] = ", ".join(main_categories)
                    row["Genres"] = genres
                    row["AgeCategory"] = age_category
                    
                    
                    
                    # Update the entire row in the Google Sheet
                    worksheet.update(range_name=f"A{idx + 2}:Z{idx + 2}", values=[list(row.values())])


                    print(f"Updated sheet: Description, Genres, MainCategory and AgeCategory for '{title}'")

                    # Add a small delay to respect API limits
                    time.sleep(1)
                except Exception as e:
                    print(f"Gemini API error: {str(e)}")
            else:
                print("No Google Books data found")
        except Exception as e:
            print(f"Google Books API error: {str(e)}")

        print("-" * 50)
        # Stop at row 500
        if ( idx >= 823):
            print("Break...Reached the end of the list. Exiting...")
            break


