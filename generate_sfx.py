#!/usr/bin/env python3
"""
Generate sound effects for button clicks using pydub
"""
from pydub import AudioSegment
from pydub.generators import Sine, Square
import os

# Create audio directory if it doesn't exist
os.makedirs('static/audio/sfx', exist_ok=True)

# 1. Button Click Sound (short, crisp)
def create_click_sound():
    # High frequency short beep
    click = Sine(2000).to_audio_segment(duration=50)
    click = click.fade_in(5).fade_out(20)
    click = click - 10  # Reduce volume
    click.export('static/audio/sfx/button_click.mp3', format='mp3')
    print("✓ Created button_click.mp3")

# 2. Next/Previous Button Sound (swoosh)
def create_nav_sound():
    # Descending tone for navigation
    nav1 = Sine(800).to_audio_segment(duration=80)
    nav2 = Sine(600).to_audio_segment(duration=60)
    nav = nav1 + nav2
    nav = nav.fade_in(10).fade_out(30)
    nav = nav - 12
    nav.export('static/audio/sfx/nav_swoosh.mp3', format='mp3')
    print("✓ Created nav_swoosh.mp3")

# 3. Mode Toggle Sound (power up)
def create_mode_sound():
    # Ascending tone for mode change
    mode1 = Sine(400).to_audio_segment(duration=60)
    mode2 = Sine(600).to_audio_segment(duration=60)
    mode3 = Sine(800).to_audio_segment(duration=60)
    mode = mode1 + mode2 + mode3
    mode = mode.fade_in(15).fade_out(30)
    mode = mode - 10
    mode.export('static/audio/sfx/mode_toggle.mp3', format='mp3')
    print("✓ Created mode_toggle.mp3")

# 4. Flip Card Sound (whoosh)
def create_flip_sound():
    # Quick sweep
    flip = Sine(1200).to_audio_segment(duration=100)
    flip = flip.fade_in(10).fade_out(50)
    flip = flip - 15
    flip.export('static/audio/sfx/card_flip.mp3', format='mp3')
    print("✓ Created card_flip.mp3")

# 5. Success/Complete Sound (chime)
def create_success_sound():
    # Pleasant chord
    note1 = Sine(523).to_audio_segment(duration=200)  # C
    note2 = Sine(659).to_audio_segment(duration=200)  # E
    note3 = Sine(784).to_audio_segment(duration=200)  # G
    success = note1.overlay(note2).overlay(note3)
    success = success.fade_in(20).fade_out(100)
    success = success - 12
    success.export('static/audio/sfx/success.mp3', format='mp3')
    print("✓ Created success.mp3")

# Generate all sounds
print("🎵 Generating sound effects...")
create_click_sound()
create_nav_sound()
create_mode_sound()
create_flip_sound()
create_success_sound()
print("\n✅ All sound effects generated!")
