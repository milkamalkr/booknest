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
#sheet_url = "https://docs.google.com/spreadsheets/d/1PBPIqC7odNqjSENr65l6yzaUg5Nb-OfipM7x5jjG2wc"
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


# Helper to check duplicates by title (case-insensitive)
def is_duplicate_title(json_array, new_title):
    return any(book.get(key_title, '').strip().lower() == new_title.strip().lower() for book in json_array)

# Build json_array from sheet records
for row in records:
    if row.get("Title (English)") and row.get("Author/Publisher"):
        # Construct the title first
        if row.get("Title in language (If not English) "):
            title = row["Title (English)"] + " (" + row["Title in language (If not English) "] + ")"
            title_local = row["Title in language (If not English) "]
        else:
            title = row["Title (English)"]
            title_local = ""

        # Check for duplicates before adding
        if not is_duplicate_title(json_array, title):
            book = {}
            book[key_sn] = cnt
            cnt += 1
            book[key_title] = title
            book[key_author] = row["Author/Publisher"]
            book[key_rent] = row.get("Expected Rent per week", 0)
            book[key_language] = row.get("Language", "")
            # keep local title if present
            if title_local:
                book["Title_Local"] = title_local
            json_array.append(book)
            print(f"Added: {title}")
        else:
            print(f"Skipped duplicate: {title}")

# Now verify against csvjson.json (compare title, author and order)
try:
    with open('csvjson.json', 'r', encoding='utf-8') as f:
        csv_data = json.load(f)
except FileNotFoundError:
    print("csvjson.json not found in current directory.")
    csv_data = None

if csv_data is None:
    print("No CSV JSON to compare. Exiting.")
else:
    # csv_data can be either {'books': [...]} or a plain list
    csv_books = csv_data.get('books') if isinstance(csv_data, dict) and 'books' in csv_data else csv_data

    # Normalize both lists to comparable dicts with 'title' and 'author'
    def normalize_sheet_book(b):
        return {
            'title': b.get(key_title, '').strip(),
            'author': b.get(key_author, '').strip()
        }

    def normalize_csv_book(b):
        return {
            'title': (b.get('title') or b.get('Book_Title') or '').strip(),
            'author': (b.get('author') or b.get('Author') or '').strip()
        }

    sheet_norm = [normalize_sheet_book(b) for b in json_array]
    csv_norm = [normalize_csv_book(b) for b in csv_books]

    total = max(len(sheet_norm), len(csv_norm))
    matches = 0
    mismatches = []

    print('\nComparing sheet -> csvjson.json (by index/order):')
    for i in range(total):
        s = sheet_norm[i] if i < len(sheet_norm) else None
        c = csv_norm[i] if i < len(csv_norm) else None

        if s and c:
            if s['title'].lower() == c['title'].lower() and s['author'].lower() == c['author'].lower():
                print(f"{i+1}: MATCH - '{s['title']}' by {s['author']}")
                matches += 1
            else:
                print(f"{i+1}: MISMATCH")
                print(f"    sheet: '{s['title']}' by {s['author']}")
                print(f"    csv:   '{c['title']}' by {c['author']}")
                mismatches.append((i+1, s, c))
        elif s and not c:
            print(f"{i+1}: MISSING in csvjson.json -> sheet has '{s['title']}' by {s['author']}")
            mismatches.append((i+1, s, None))
        elif c and not s:
            print(f"{i+1}: EXTRA in csvjson.json -> csv has '{c['title']}' by {c['author']}")
            mismatches.append((i+1, None, c))

    print('\nSummary:')
    print(f"Total compared positions: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches / differences: {len(mismatches)}")


