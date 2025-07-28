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
sheet_url = "https://docs.google.com/spreadsheets/d/1-2DR7sqGwSf56iBk9Hnhu7Xfj5XxDapsODdivvVxNmI"
sheet = client.open_by_url(sheet_url)

# Select worksheet by name or index
worksheet = sheet.get_worksheet(0)  # or use .worksheet("Sheet1")

# Read all data as a list of lists
data = worksheet.get_all_values()

# Print the data
for row in data:
    print("================================\n")
    print(row)
 
# Get all rows as list of dicts (header must be present)
records = worksheet.get_all_records()

# Create JSON array with the required format
json_data = {"books": []}

for row in records:
    if row.get("Title (English)") and row.get("Author/Publisher"):
        book = {
            "title": row["Title (English)"],
            "author": row["Author/Publisher"],
            "rent_per_week": row.get("Expected Rent per week", 0),
            "owner_id": row.get("book_owner_id"),  # Default owner ID
            "status": "available",
            "value": row.get("Book Value", 299),  # Default value if not provided
            "published_year": row.get("Published Year", 2000),  # Default year if not provided
            "image_url": "",  # Can be updated later
            "description": row.get("Description", "."),
            "tags": [],  # Can be populated based on categories if available
            "language": row.get("Language", "English"),
            "title_local": row.get("Title in language (If not English) ", "")
        }
        
        # Add tags if available in the sheet
        if row.get("Categories"):
            book["tags"] = [tag.strip().lower() for tag in row["Categories"].split(",")]
        
        json_data["books"].append(book)

# Print formatted JSON
print(json.dumps(json_data, indent=2, ensure_ascii=False))

# Optionally save to file
with open("post_books.json", "w", encoding="utf-8") as f:
     json.dump(json_data, f, indent=2, ensure_ascii=False)