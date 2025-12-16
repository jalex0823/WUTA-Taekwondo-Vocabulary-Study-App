"""
Generate belt images with symbolic meanings
Based on https://atlantatkd.com/the-meaning-behind-the-color-of-each-belt-rank-in-tae-kwon-do/
"""

def create_belt_svg(belt_name, belt_color, tip_color, meaning, filename):
    """Create a belt image with meaning text"""
    
    # Color mapping for belts
    color_map = {
        'white': '#FFFFFF',
        'yellow': '#FFD700',
        'green': '#4CAF50',
        'blue': '#2196F3',
        'red': '#F44336',
        'brown': '#795548',
        'black': '#212121'
    }
    
    main_color = color_map.get(belt_color.lower(), '#CCCCCC')
    tip = color_map.get(tip_color.lower() if tip_color else '', None)
    
    # Create SVG with belt illustration and meaning
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
  <!-- Background gradient -->
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f8f9fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e9ecef;stop-opacity:1" />
    </linearGradient>
    
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <rect width="400" height="300" fill="url(#bgGrad)"/>
  
  <!-- Belt illustration -->
  <g id="belt" filter="url(#shadow)">
    <!-- Main belt body -->
    <rect x="50" y="80" width="300" height="60" rx="8" fill="{main_color}" stroke="#333" stroke-width="2"/>
    
    <!-- Belt texture lines -->
    <line x1="70" y1="90" x2="330" y2="90" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>
    <line x1="70" y1="130" x2="330" y2="130" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>
    
    <!-- Belt ends -->
    <rect x="45" y="140" width="30" height="80" rx="4" fill="{main_color}" stroke="#333" stroke-width="2"/>
    <rect x="325" y="140" width="30" height="80" rx="4" fill="{main_color}" stroke="#333" stroke-width="2"/>
'''
    
    # Add black tip if applicable
    if tip:
        svg += f'''    
    <!-- Black tip on right end -->
    <rect x="325" y="140" width="30" height="30" rx="4" fill="{tip}"/>
'''
    
    svg += f'''    
    <!-- Knot in center -->
    <ellipse cx="200" cy="110" rx="25" ry="30" fill="{main_color}" stroke="#333" stroke-width="2"/>
    <ellipse cx="200" cy="110" rx="15" ry="20" fill="rgba(0,0,0,0.1)"/>
  </g>
  
  <!-- Belt name -->
  <text x="200" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#2c3e50" text-anchor="middle">{belt_name}</text>
  
  <!-- Meaning text -->
  <text x="200" y="250" font-family="Arial, sans-serif" font-size="14" fill="#495057" text-anchor="middle" font-style="italic">"{meaning}"</text>
  
  <!-- Decorative elements -->
  <circle cx="30" cy="30" r="3" fill="#667eea" opacity="0.3"/>
  <circle cx="370" cy="270" r="3" fill="#667eea" opacity="0.3"/>
  <circle cx="370" cy="30" r="2" fill="#764ba2" opacity="0.3"/>
  <circle cx="30" cy="270" r="2" fill="#764ba2" opacity="0.3"/>
</svg>'''
    
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

# Belt meanings from Atlanta TKD
belt_meanings = {
    'white': 'Purity, a new beginning, no prior knowledge',
    'white_tip': 'Foundation building begins',
    'yellow': 'Earth from which plants grow, foundation stage',
    'yellow_tip': 'Growing roots and strength',
    'green': 'Growing in strength and maturity',
    'green_tip': 'Reaching upward, solid skills',
    'blue': 'Sky and new heights, continued progress',
    'blue_tip': 'Mental and emotional growth',
    'red': 'Sun, tremendous power and energy',
    'red_tip': 'Strength balanced with control',
    'brown': 'Transition to mastery',
    'brown_tip': 'Final preparation for black belt',
    'black': 'Proficiency, maturity, new beginning'
}

print("Creating belt images with meanings...")
print("=" * 50)

base_path = "/Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App/static/images/belts"

import os
os.makedirs(base_path, exist_ok=True)

# Create images for each belt level
create_belt_svg('White Belt', 'white', None, belt_meanings['white'], f'{base_path}/white.svg')
create_belt_svg('White Belt - Black Tip', 'white', 'black', belt_meanings['white_tip'], f'{base_path}/white_tip.svg')
create_belt_svg('Yellow Belt', 'yellow', None, belt_meanings['yellow'], f'{base_path}/yellow.svg')
create_belt_svg('Yellow Belt - Black Tip', 'yellow', 'black', belt_meanings['yellow_tip'], f'{base_path}/yellow_tip.svg')
create_belt_svg('Green Belt', 'green', None, belt_meanings['green'], f'{base_path}/green.svg')
create_belt_svg('Green Belt - Black Tip', 'green', 'black', belt_meanings['green_tip'], f'{base_path}/green_tip.svg')
create_belt_svg('Blue Belt', 'blue', None, belt_meanings['blue'], f'{base_path}/blue.svg')
create_belt_svg('Blue Belt - Black Tip', 'blue', 'black', belt_meanings['blue_tip'], f'{base_path}/blue_tip.svg')
create_belt_svg('Red Belt', 'red', None, belt_meanings['red'], f'{base_path}/red.svg')
create_belt_svg('Red Belt - Black Tip', 'red', 'black', belt_meanings['red_tip'], f'{base_path}/red_tip.svg')
create_belt_svg('Brown Belt', 'brown', None, belt_meanings['brown'], f'{base_path}/brown.svg')
create_belt_svg('Brown Belt - Black Tip', 'brown', 'black', belt_meanings['brown_tip'], f'{base_path}/brown_tip.svg')
create_belt_svg('Black Belt', 'black', None, belt_meanings['black'], f'{base_path}/black.svg')

print("=" * 50)
print(f"✅ Created 13 belt images with meanings!")
print(f"\nImages saved to: {base_path}/")
