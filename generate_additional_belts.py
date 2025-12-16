"""
Generate belt images for orange and purple belts (additional WUTA levels)
"""

def create_belt_svg(belt_name, belt_color, tip_color, meaning, filename):
    """Create a belt image with meaning text"""
    
    # Color mapping for belts
    color_map = {
        'white': '#FFFFFF',
        'yellow': '#FFD700',
        'orange': '#FF8C00',
        'green': '#4CAF50',
        'blue': '#2196F3',
        'purple': '#9C27B0',
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

print("Creating orange and purple belt images...")
print("=" * 50)

base_path = "/Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App/static/images/belts"

# Orange belt - transition between yellow and green
create_belt_svg('Orange Belt', 'orange', None, 
                'Warmth of the sun, energy and enthusiasm',
                f'{base_path}/orange.svg')

create_belt_svg('Orange Belt - Black Tip', 'orange', 'black',
                'Growing confidence and skill',
                f'{base_path}/orange_tip.svg')

# Purple belt - transition between blue and red
create_belt_svg('Purple Belt', 'purple', None,
                'Dignity and honor, approaching mastery',
                f'{base_path}/purple.svg')

create_belt_svg('Purple Belt - Black Tip', 'purple', 'black',
                'Advanced skills and leadership',
                f'{base_path}/purple_tip.svg')

print("=" * 50)
print("✅ Created 4 additional belt images!")
