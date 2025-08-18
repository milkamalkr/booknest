import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

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
key_description = "Description"
key_age_category = "Age_category"
key_genre = "Genre"


# Add this helper function before the main loop
def is_duplicate_title(json_array, new_title):
    """Check if a book with the same title exists in json_array"""
    return any(book[key_title].lower() == new_title.lower() for book in json_array)

# Initialize a global set to collect all genres
all_genres = set()

# Modify the main loop
for row in records:
    if row.get("Title (English)") and row["Author/Publisher"]:
        # Construct the title first
        if row.get("Title in language (If not English) "):
            title = row["Title (English)"] + " (" + row["Title in language (If not English) "] + ")"
        else:    
            title = row["Title (English)"]
            
        # Check for duplicates before adding
        if not is_duplicate_title(json_array, title):
            book = {}
            book[key_sn] = cnt
            cnt += 1
            book[key_title] = title
            book[key_author] = row["Author/Publisher"]
            book[key_rent] = row["Expected Rent per week"]
            book[key_language] = row["Language"]
            book[key_description] = row["Description"]
            
            # Collect genres and add to global set
            genres = row["Genres"].split(",") if row["Genres"] else []
            genres = [genre.strip() for genre in genres]
            book[key_genre] = genres
            all_genres.update(genres)

            book[key_age_category] = row["AgeCategory"]
            json_array.append(book)
            print(f"Added: {title}")
        else:
            print(f"Skipped duplicate: {title}")

# Create the final JSON structure
final_json = {
    "all_genres": sorted(list(all_genres)),  # Sort genres alphabetically
    "age_groups":["Toddler ","Children ","Teenage ","Young Adult ","Adult "],
    "languages":["English", "Malayalam", "Tamil"],
    "all_books": json_array
}

# Save to file
with open("csvjson.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, indent=2, ensure_ascii=False)