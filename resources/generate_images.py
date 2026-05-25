#!/usr/bin/env python3
"""Generate themed SVG lesson illustrations for NCE Book 1 Lessons 1-20."""

LESSONS = [
    (1, "Excuse me!", "👜", "#E3F2FD", "#1565C0", "handbag"),
    (2, "Is this your…?", "📚", "#E8F5E9", "#2E7D32", "book"),
    (3, "Sorry, sir.", "☂️", "#F3E5F5", "#6A1B9A", "umbrella"),
    (4, "Is this your…?", "🖊️", "#FFF3E0", "#E65100", "pen"),
    (5, "Nice to meet you.", "👋", "#E0F7FA", "#00838F", "greeting"),
    (6, "What nationality?", "🌍", "#FBE9E7", "#BF360C", "world"),
    (7, "Are you a teacher?", "👩‍🏫", "#F1F8E9", "#33691E", "teacher"),
    (8, "What's your job?", "👮", "#E8EAF6", "#283593", "policeman"),
    (9, "How are you?", "😊", "#FFF8E1", "#FF6F00", "happy"),
    (10, "Look at…", "👀", "#FCE4EC", "#AD1457", "look"),
    (11, "Is this your shirt?", "👗", "#EDE7F6", "#4527A0", "dress"),
    (12, "What colour?", "🎨", "#E0F2F1", "#00695C", "colour"),
    (13, "A new dress", "👠", "#FFF3E0", "#E65100", "dress"),
    (14, "Whose is this?", "👔", "#E3F2FD", "#0D47A1", "shirt"),
    (15, "Your passports!", "🛂", "#E8F5E9", "#1B5E20", "passport"),
    (16, "Are they…?", "📸", "#F3E5F5", "#4A148C", "tourist"),
    (17, "How do you do?", "🤝", "#E0F7FA", "#006064", "handshake"),
    (18, "What are their jobs?", "⌨️", "#FFF8E1", "#F57F17", "keyboard"),
    (19, "Tired and thirsty", "😮‍💨", "#FBE9E7", "#B71C1C", "tired"),
    (20, "Big and small", "🏪", "#E8EAF6", "#1A237E", "shop"),
]


def generate_svg(num, title, emoji, bg_color, accent_color, theme):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <defs>
    <linearGradient id="bg{num}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow{num}">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.1"/>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="300" fill="url(#bg{num})" rx="12"/>
  
  <!-- Decorative circle -->
  <circle cx="340" cy="40" r="60" fill="{accent_color}" opacity="0.08"/>
  <circle cx="60" cy="260" r="40" fill="{accent_color}" opacity="0.06"/>
  
  <!-- Emoji -->
  <text x="200" y="115" text-anchor="middle" font-size="64" filter="url(#shadow{num})">{emoji}</text>
  
  <!-- Lesson number -->
  <rect x="150" y="135" width="100" height="32" rx="16" fill="{accent_color}"/>
  <text x="200" y="157" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="white">Lesson {num}</text>
  
  <!-- Title -->
  <text x="200" y="200" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="600" fill="#333333">{title}</text>
  
  <!-- Subtitle -->
  <text x="200" y="230" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#888888">新概念英语第一册 · New Concept English</text>
  
  <!-- Bottom decoration -->
  <rect x="160" y="255" width="80" height="4" rx="2" fill="{accent_color}" opacity="0.3"/>
</svg>'''


if __name__ == "__main__":
    import os
    os.makedirs("images", exist_ok=True)
    
    for num, title, emoji, bg, accent, theme in LESSONS:
        filename = f"images/lesson_{num:03d}.svg"
        svg = generate_svg(num, title, emoji, bg, accent, theme)
        with open(filename, "w") as f:
            f.write(svg)
        print(f"✓ Generated {filename}")
    
    print(f"\n✅ Generated {len(LESSONS)} lesson illustrations!")
