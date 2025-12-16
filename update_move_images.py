#!/usr/bin/env python3
"""
Update move image paths in terms.json with specific visualizations
"""
import json

# Read the data
with open('data/terms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mapping of move IDs to their specific visualization paths
move_visualizations = {
    # Kicks
    'ap_chagi': '/static/images/moves/kicks/ap_chagi.svg',
    'dollyo_chagi': '/static/images/moves/kicks/dollyo_chagi.svg',
    'yeop_chagi': '/static/images/moves/kicks/yeop_chagi.svg',
    
    # Blocks
    'arae_makgi': '/static/images/moves/blocks/arae_makgi.svg',
    
    # Strikes/Punches
    'jirugi': '/static/images/moves/strikes/jirugi.svg',
    'momtong_jirugi': '/static/images/moves/strikes/jirugi.svg',
    'olgul_jirugi': '/static/images/moves/strikes/jirugi.svg',
    
    # Stances
    'ap_seogi': '/static/images/moves/stances/ap_seogi.svg',
}

# Update the image paths
updated_count = 0
for belt in data['belts']:
    for term in belt['terms']:
        if term['id'] in move_visualizations:
            old_path = term.get('image_path', '')
            new_path = move_visualizations[term['id']]
            if old_path != new_path:
                term['image_path'] = new_path
                updated_count += 1
                print(f"✓ Updated {term['id']}: {term['english']}")

# Write back to file
with open('data/terms.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Updated {updated_count} move visualizations!")
