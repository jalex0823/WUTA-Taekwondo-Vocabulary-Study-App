"""
Generate placeholder SVG images for Taekwondo moves
These are simple stick figure representations to help visualize techniques
"""

def create_stance_svg(name, filename):
    """Create a simple stance illustration"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
  <!-- Background -->
  <rect width="300" height="400" fill="#f8f9fa"/>
  <rect width="300" height="40" fill="#667eea" opacity="0.2"/>
  
  <!-- Title -->
  <text x="150" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#667eea" text-anchor="middle">{name}</text>
  
  <!-- Grid lines for reference -->
  <line x1="150" y1="60" x2="150" y2="380" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="20" y1="220" x2="280" y2="220" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="5,5"/>
  
  <!-- Stick figure in stance position -->
  <g id="figure">
    <!-- Head -->
    <circle cx="150" cy="100" r="20" fill="none" stroke="#2c3e50" stroke-width="3"/>
    
    <!-- Body -->
    <line x1="150" y1="120" x2="150" y2="220" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Stance-specific leg positions will be added per stance -->
  </g>
  
  <!-- Footprint markers -->
  <ellipse cx="120" cy="360" rx="25" ry="35" fill="#667eea" opacity="0.3" transform="rotate(-20 120 360)"/>
  <ellipse cx="180" cy="360" rx="25" ry="35" fill="#667eea" opacity="0.3" transform="rotate(20 180 360)"/>
  
  <!-- Label -->
  <rect x="50" y="370" width="200" height="25" fill="white" stroke="#667eea" stroke-width="2" rx="5"/>
  <text x="150" y="388" font-family="Arial" font-size="14" fill="#667eea" text-anchor="middle">Stance</text>
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

def create_kick_svg(name, filename):
    """Create a simple kick illustration"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
  <!-- Background -->
  <rect width="300" height="400" fill="#f8f9fa"/>
  <rect width="300" height="40" fill="#FF6B6B" opacity="0.2"/>
  
  <!-- Title -->
  <text x="150" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#FF6B6B" text-anchor="middle">{name}</text>
  
  <!-- Motion lines -->
  <path d="M 200 180 Q 220 160 240 140" stroke="#FFD93D" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>
  <path d="M 205 190 Q 230 170 250 150" stroke="#FFD93D" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.4"/>
  
  <!-- Stick figure kicking -->
  <g id="figure">
    <!-- Head -->
    <circle cx="120" cy="100" r="20" fill="none" stroke="#2c3e50" stroke-width="3"/>
    
    <!-- Body (leaning) -->
    <line x1="120" y1="120" x2="110" y2="200" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Arms (balance) -->
    <line x1="110" y1="160" x2="60" y2="140" stroke="#2c3e50" stroke-width="3" stroke-linecap="round"/>
    <line x1="110" y1="160" x2="90" y2="190" stroke="#2c3e50" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Standing leg -->
    <line x1="110" y1="200" x2="100" y2="280" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="100" y1="280" x2="90" y2="320" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Kicking leg (extended) -->
    <line x1="110" y1="200" x2="180" y2="160" stroke="#FF6B6B" stroke-width="5" stroke-linecap="round"/>
    <line x1="180" y1="160" x2="240" y2="140" stroke="#FF6B6B" stroke-width="5" stroke-linecap="round"/>
    
    <!-- Impact marker -->
    <circle cx="240" cy="140" r="15" fill="none" stroke="#FFD93D" stroke-width="3"/>
    <circle cx="240" cy="140" r="20" fill="none" stroke="#FFD93D" stroke-width="2" opacity="0.5"/>
  </g>
  
  <!-- Label -->
  <rect x="50" y="370" width="200" height="25" fill="white" stroke="#FF6B6B" stroke-width="2" rx="5"/>
  <text x="150" y="388" font-family="Arial" font-size="14" fill="#FF6B6B" text-anchor="middle">Kick</text>
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

def create_block_svg(name, filename):
    """Create a simple block illustration"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
  <!-- Background -->
  <rect width="300" height="400" fill="#f8f9fa"/>
  <rect width="300" height="40" fill="#4ECDC4" opacity="0.2"/>
  
  <!-- Title -->
  <text x="150" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#4ECDC4" text-anchor="middle">{name}</text>
  
  <!-- Incoming attack (blocked) -->
  <line x1="250" y1="120" x2="180" y2="140" stroke="#e74c3c" stroke-width="4" stroke-linecap="round" stroke-dasharray="8,4"/>
  <path d="M 260 110 L 250 120 L 260 130" stroke="#e74c3c" stroke-width="3" fill="none"/>
  
  <!-- Shield/block effect -->
  <ellipse cx="170" cy="140" rx="30" ry="40" fill="#4ECDC4" opacity="0.2" stroke="#4ECDC4" stroke-width="2"/>
  
  <!-- Stick figure blocking -->
  <g id="figure">
    <!-- Head -->
    <circle cx="150" cy="90" r="20" fill="none" stroke="#2c3e50" stroke-width="3"/>
    
    <!-- Body -->
    <line x1="150" y1="110" x2="150" y2="210" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Blocking arm (raised) -->
    <line x1="150" y1="130" x2="170" y2="110" stroke="#4ECDC4" stroke-width="5" stroke-linecap="round"/>
    <line x1="170" y1="110" x2="180" y2="140" stroke="#4ECDC4" stroke-width="5" stroke-linecap="round"/>
    
    <!-- Other arm -->
    <line x1="150" y1="130" x2="120" y2="160" stroke="#2c3e50" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Legs -->
    <line x1="150" y1="210" x2="130" y2="280" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="130" y1="280" x2="120" y2="320" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="150" y1="210" x2="170" y2="280" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="170" y1="280" x2="180" y2="320" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
  </g>
  
  <!-- Impact stars -->
  <text x="190" y="135" font-size="24" fill="#FFD93D">⭐</text>
  <text x="175" y="160" font-size="18" fill="#FFD93D">✨</text>
  
  <!-- Label -->
  <rect x="50" y="370" width="200" height="25" fill="white" stroke="#4ECDC4" stroke-width="2" rx="5"/>
  <text x="150" y="388" font-family="Arial" font-size="14" fill="#4ECDC4" text-anchor="middle">Block</text>
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

def create_strike_svg(name, filename):
    """Create a simple strike illustration"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
  <!-- Background -->
  <rect width="300" height="400" fill="#f8f9fa"/>
  <rect width="300" height="40" fill="#9b59b6" opacity="0.2"/>
  
  <!-- Title -->
  <text x="150" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#9b59b6" text-anchor="middle">{name}</text>
  
  <!-- Motion lines -->
  <path d="M 100 150 L 220 160" stroke="#FFD93D" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>
  <path d="M 100 160 L 230 170" stroke="#FFD93D" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.4"/>
  
  <!-- Stick figure striking -->
  <g id="figure">
    <!-- Head -->
    <circle cx="120" cy="100" r="20" fill="none" stroke="#2c3e50" stroke-width="3"/>
    
    <!-- Body (twisted) -->
    <line x1="120" y1="120" x2="130" y2="200" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Striking arm (extended) -->
    <line x1="130" y1="150" x2="180" y2="160" stroke="#9b59b6" stroke-width="5" stroke-linecap="round"/>
    <line x1="180" y1="160" x2="240" y2="165" stroke="#9b59b6" stroke-width="5" stroke-linecap="round"/>
    
    <!-- Fist -->
    <circle cx="245" cy="165" r="8" fill="#9b59b6"/>
    
    <!-- Other arm (chambered) -->
    <line x1="130" y1="150" x2="100" y2="170" stroke="#2c3e50" stroke-width="3" stroke-linecap="round"/>
    <line x1="100" y1="170" x2="80" y2="180" stroke="#2c3e50" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Legs (stable stance) -->
    <line x1="130" y1="200" x2="110" y2="280" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="110" y1="280" x2="100" y2="320" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="130" y1="200" x2="150" y2="280" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    <line x1="150" y1="280" x2="160" y2="320" stroke="#2c3e50" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Impact effect -->
    <circle cx="245" cy="165" r="12" fill="none" stroke="#FFD93D" stroke-width="3"/>
    <circle cx="245" cy="165" r="18" fill="none" stroke="#FFD93D" stroke-width="2" opacity="0.5"/>
    <line x1="255" y1="165" x2="270" y2="165" stroke="#FFD93D" stroke-width="2"/>
    <line x1="250" y1="155" x2="260" y2="145" stroke="#FFD93D" stroke-width="2"/>
    <line x1="250" y1="175" x2="260" y2="185" stroke="#FFD93D" stroke-width="2"/>
  </g>
  
  <!-- Label -->
  <rect x="50" y="370" width="200" height="25" fill="white" stroke="#9b59b6" stroke-width="2" rx="5"/>
  <text x="150" y="388" font-family="Arial" font-size="14" fill="#9b59b6" text-anchor="middle">Strike</text>
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

def create_form_svg(name, filename):
    """Create a simple form illustration"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
  <!-- Background -->
  <rect width="300" height="400" fill="#f8f9fa"/>
  <rect width="300" height="40" fill="#e67e22" opacity="0.2"/>
  
  <!-- Title -->
  <text x="150" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#e67e22" text-anchor="middle">{name}</text>
  
  <!-- Movement path -->
  <path d="M 80 180 L 120 140 L 180 140 L 220 180 L 180 220 L 120 220 Z" 
        stroke="#e67e22" stroke-width="3" fill="none" stroke-dasharray="10,5" opacity="0.5"/>
  
  <!-- Multiple position silhouettes (form sequence) -->
  <g opacity="0.3">
    <circle cx="80" cy="180" r="8" fill="#2c3e50"/>
    <line x1="80" y1="188" x2="80" y2="210" stroke="#2c3e50" stroke-width="2"/>
  </g>
  
  <g opacity="0.5">
    <circle cx="120" cy="140" r="8" fill="#2c3e50"/>
    <line x1="120" y1="148" x2="120" y2="170" stroke="#2c3e50" stroke-width="2"/>
  </g>
  
  <!-- Main figure (current position) -->
  <g id="figure">
    <!-- Head -->
    <circle cx="150" cy="120" r="20" fill="none" stroke="#e67e22" stroke-width="3"/>
    
    <!-- Body -->
    <line x1="150" y1="140" x2="150" y2="220" stroke="#e67e22" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Arms in form position -->
    <line x1="150" y1="160" x2="110" y2="140" stroke="#e67e22" stroke-width="3" stroke-linecap="round"/>
    <line x1="150" y1="160" x2="190" y2="180" stroke="#e67e22" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Legs in form stance -->
    <line x1="150" y1="220" x2="130" y2="280" stroke="#e67e22" stroke-width="4" stroke-linecap="round"/>
    <line x1="130" y1="280" x2="120" y2="320" stroke="#e67e22" stroke-width="4" stroke-linecap="round"/>
    <line x1="150" y1="220" x2="170" y2="280" stroke="#e67e22" stroke-width="4" stroke-linecap="round"/>
    <line x1="170" y1="280" x2="180" y2="320" stroke="#e67e22" stroke-width="4" stroke-linecap="round"/>
  </g>
  
  <!-- Sequence indicators -->
  <circle cx="80" cy="360" r="6" fill="#e67e22"/>
  <circle cx="120" cy="360" r="6" fill="#e67e22"/>
  <circle cx="150" cy="360" r="8" fill="#e67e22" stroke="#e67e22" stroke-width="2"/>
  <circle cx="180" cy="360" r="6" fill="#e67e22" opacity="0.5"/>
  <circle cx="220" cy="360" r="6" fill="#e67e22" opacity="0.3"/>
  
  <!-- Label -->
  <rect x="50" y="370" width="200" height="25" fill="white" stroke="#e67e22" stroke-width="2" rx="5"/>
  <text x="150" y="388" font-family="Arial" font-size="14" fill="#e67e22" text-anchor="middle">Poomsae/Form</text>
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Created {filename}")

# Create generic placeholder images for each category
print("Creating placeholder images for Taekwondo techniques...")
print("=" * 50)

base_path = "/Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App/static/images/moves"

# Stances
create_stance_svg("Stance", f"{base_path}/stances/default_stance.svg")

# Kicks
create_kick_svg("Kick", f"{base_path}/kicks/default_kick.svg")

# Blocks
create_block_svg("Block", f"{base_path}/blocks/default_block.svg")

# Strikes
create_strike_svg("Strike", f"{base_path}/strikes/default_strike.svg")

# Forms
create_form_svg("Form", f"{base_path}/forms/default_form.svg")

print("=" * 50)
print("✅ Created 5 placeholder SVG images!")
print("\nThese generic images will be used for all moves in each category.")
print("You can replace them with specific technique photos or illustrations later.")
