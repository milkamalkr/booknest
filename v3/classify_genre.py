from google import genai
import os
import json
# -------------------------------
# 1. Configure your Gemini API Key
# -------------------------------
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise ValueError("Environment variable GEMINI_KEY is not set.")

#genai.configure(api_key=api_key)


# -------------------------------
# 2. Define the 20 Main Categories
# -------------------------------
MAIN_CATEGORIES = [
    "Fiction",
    "Fantasy",
    "Science Fiction & Technology",
    "Mystery, Thriller & Suspense",
    "Romance",
    "Horror & Supernatural",
    "Poetry & Drama",
    "Biography & Memoir",
    "History & Culture",
    "Religion, Philosophy & Spirituality",
    "Psychology & Self-Help",
    "Business, Economics & Management",
    "Education & Learning",
    "Science & Mathematics",
    "Health, Medicine & Wellness",
    "Social Sciences & Studies",
    "Politics & Current Affairs",
    "Literary Studies & Criticism",
    "Lifestyle & Practical Guides",
    "Entertainment, Sports & Hobbies",
    "Others"
]

# -------------------------------
# 3. Gemini Model Initialization
# -------------------------------
#model = genai.GenerativeModel("gemini-1.5-flash")  # use "gemini-pro" if you prefer

# -------------------------------
# 4. Function to classify a genre
# -------------------------------
def classify_genre(genre: str, genaiclient, classified_json) -> str:
    # First, check if genre exists in classified_json
    for category_obj in classified_json:
        if genre in category_obj.get("sub_categories", []):
            return category_obj.get("main_Category")

    prompt = f"""
    Classify the following genre into exactly one of the 20 main categories below.
    If uncertain, choose the closest match and call out it is a closest match only.
    Always classify under 'Fiction' if the Genre has 'Fiction' word in it
    Always classify the following genres under 'Others':
       - LGBTQ+ themes
       - Coming-of-Age Story
       - Coming-of-age
       - Graphic Novel
    Always classify the following genres under 'Entertainment, Sports & Hobbies'
       - Adventure
       - Friendship
       - Humor
       - Family Saga
       - Movie Novelization
       - Satire
       - Short Story Collection

    Genre: "{genre}"

    Categories: {MAIN_CATEGORIES}

    Respond with ONLY the category name.
    """

    response = genaiclient.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

# -------------------------------
# 5. Example usage
# -------------------------------
# Load all_genres from csvjson.json
# with open("csvjson.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     test_genres = data.get("all_genres", [])
#     #test_genres = ['War Fiction', 'Adventure fiction', "Women's Fiction"]

# Add all genres to classified_genre as objects with main categories and subcategories
classified_genre = {}

if __name__ == "__main__":
    test_genres = ["Juvenile Fiction", "Career Guidance","Dark Humor", "Tailoring classes"]
    client = genai.Client(api_key="AIzaSyB9wgZzpxY_4Imak8rwWLasi1o7By541mU")

    with open("classified_genres.json", "r", encoding="utf-8") as f:
        classified_json = json.load(f)

    for g in test_genres:
        category = classify_genre(g, client, classified_json)
        print(f"{g} → {category}")
    #     if category not in classified_genre:
    #         classified_genre[category] = []
    #     classified_genre[category].append(g)

    # # Convert classified_genre to the desired array of objects format
    # classified_genre_array = [{"main_Category": key, "sub_categories": value} for key, value in classified_genre.items()]

    # # Save classified_genre_array to a JSON file
    # with open("classified_genres.json", "w", encoding="utf-8") as f:
    #     json.dump(classified_genre_array, f, indent=4, ensure_ascii=False)

    # print("Full genre classification saved to classified_genres.json.")

