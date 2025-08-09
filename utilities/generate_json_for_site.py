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
sheet_url = "https://docs.google.com/spreadsheets/d/1Lp66xVcGh7nshszkunAlQKEoPj-CHvJ8PZ_6Yp0g2mU"

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

# Add this helper function before the main loop
def is_duplicate_title(json_array, new_title):
    """Check if a book with the same title exists in json_array"""
    return any(book[key_title].lower() == new_title.lower() for book in json_array)

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
            json_array.append(book)
            print(f"Added: {title}")
        else:
            print(f"Skipped duplicate: {title}")


# Print or write to file
#print(json.dumps(json_array, indent=2, ensure_ascii=False))

# Optionally save to file
with open("csvjson.json", "w", encoding="utf-8") as f:
     json.dump(json_array, f, indent=2, ensure_ascii=False)