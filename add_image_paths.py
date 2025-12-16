"""
Add image_path field to move terms in terms.json
Maps each technique to the appropriate placeholder image
"""
import json

# Load terms data
with open('data/terms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Category to image path mapping
image_map = {
    "Stance": "/static/images/moves/stances/default_stance.svg",
    "Kick": "/static/images/moves/kicks/default_kick.svg",
    "Block": "/static/images/moves/blocks/default_block.svg",
    "Strike": "/static/images/moves/strikes/default_strike.svg",
    "Form": "/static/images/moves/forms/default_form.svg"
}

# Count terms updated
updated_count = 0

# Iterate through all belts and terms
for belt in data['belts']:
    for term in belt['terms']:
        # If term has a move category and doesn't already have an image_path
        if term['category'] in image_map and 'image_path' not in term:
            term['image_path'] = image_map[term['category']]
            updated_count += 1
            print(f"✅ Added image to: {term['english']} ({term['category']})")

# Save updated data back to file
with open('data/terms.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 50)
print(f"✅ Updated {updated_count} terms with image paths!")
print("=" * 50)
