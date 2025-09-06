import json

# Load all_books from csvjson.json
with open("csvjson.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    all_books = data.get("all_books", [])

# Load classified_genre.json
with open("classified_genres.json", "r", encoding="utf-8") as f:
    classified_genres = json.load(f)

# Iterate over all books and add main_categories
for book in all_books:
    print(book['Book_Title'])
    book_genres = book.get("Genre", [])
    #print(book_genres)
    main_categories = set()
    for genre in book_genres:
        for entry in classified_genres:
            #print(genre)
            if genre in entry.get("sub_categories", []):
                main_categories.add(entry.get("main_Category"))
                print(f"{genre} → {entry.get('main_Category')}")
                #print(main_categories)
    book["main_categories"] = list(main_categories)
    #break

# Create an object to store the final data
output_object = {
    "age_groups": data.get("age_groups", []),
    "all_languages": data.get("all_languages", []),
    "all_books": all_books,
    "classified_genres": classified_genres
}

# Write the object to updated_books.json
with open("updated_books.json", "w", encoding="utf-8") as f:
    json.dump(output_object, f, indent=4, ensure_ascii=False)

print("Updated object with age_groups, all_languages, all_books, and classified_genres saved to updated_books.json.")
