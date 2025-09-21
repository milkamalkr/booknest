import json

# filepath: d:\BookNest\fastapi-pytest\booknest\v2\update_classified_genres.py
def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def update_classified_genres(source_file, target_file, output_file):
    """Update classified_genre_exis.json with missing sub_categories from classified_genres.json."""
    # Load source and target JSON files
    source_data = load_json(source_file)
    target_data = load_json(target_file)

    # Create a dictionary for quick lookup of main categories in the target file
    target_dict = {item["main_Category"]: item for item in target_data}

    # Iterate through each main category in the source file
    for source_item in source_data:
        main_category = source_item["main_Category"]
        source_sub_categories = {sub.strip().lower() for sub in source_item.get("sub_categories", [])}

        # Check if the main category exists in the target file
        if main_category in target_dict:
            target_item = target_dict[main_category]
            target_sub_categories = {sub.strip().lower() for sub in target_item.get("sub_categories", [])}

            # Find missing sub_categories
            missing_sub_categories = source_sub_categories - target_sub_categories

            # Add missing sub_categories to the target
            if missing_sub_categories:
                print(f"Adding missing sub_categories to '{main_category}': {missing_sub_categories}")
                target_item["sub_categories"].extend(
                    sub for sub in source_item.get("sub_categories", []) if sub.strip().lower() in missing_sub_categories
                )
        else:
            # If the main category doesn't exist, add the entire item to the target
            print(f"Adding new main category '{main_category}' with sub_categories.")
            target_data.append(source_item)

    # Save the updated target data to the output file
    save_json(target_data, output_file)
    print(f"Updated classified genres saved to {output_file}")

if __name__ == "__main__":
    # File paths
    source_file = "classified_genres.json"
    target_file = "classified_genre_exis.json"
    output_file = "updated_classified_genres.json"

    # Update classified genres
    update_classified_genres(source_file, target_file, output_file)