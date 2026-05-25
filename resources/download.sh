#!/bin/bash
# Download NCE Book 1 audio & LRC from wychl/nce GitHub repo
# Source: https://github.com/wychl/nce
# Audio: US English version, paired files (1&2, 3&4, etc.)
# LRC: Synchronized lyrics with sentence timestamps

BASE_URL="https://raw.githubusercontent.com/wychl/nce/main/us/NCE1"
AUDIO_DIR="audio"
LRC_DIR="lrc"

mkdir -p "$AUDIO_DIR" "$LRC_DIR"

# Paired audio files for Lessons 1-20
declare -A FILES
FILES["001&002.Excuse Me"]="001&002.Excuse Me"
FILES["003&004.Sorry, Sir"]="003&004.Sorry, Sir"
FILES["005&006.Nice to Meet You"]="005&006.Nice to Meet You"
FILES["007&008.Are You a Teacher"]="007&008.Are You a Teacher"
FILES["009&010.How Are You Today"]="009&010.How Are You Today"
FILES["011&012.Is This Your Shirt"]="011&012.Is This Your Shirt"
FILES["013&014.A New Dress"]="013&014.A New Dress"
FILES["015&016.Your Passports, Please"]="015&016.Your Passports, Please"
FILES["017&018.How do you do"]="017&018.How do you do"
FILES["019&020.Tired and Thirsty"]="019&020.Tired and Thirsty"

for name in "${!FILES[@]}"; do
  # URL encode for download
  encoded=$(echo "$name" | python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.stdin.read().strip()))")
  
  # Download MP3
  if [ ! -f "$AUDIO_DIR/$name.mp3" ] || [ ! -s "$AUDIO_DIR/$name.mp3" ]; then
    echo "Downloading: $name.mp3"
    curl -sL -o "$AUDIO_DIR/$name.mp3" "$BASE_URL/$encoded.mp3"
  fi
  
  # Download LRC
  if [ ! -f "$LRC_DIR/$name.lrc" ] || [ ! -s "$LRC_DIR/$name.lrc" ]; then
    echo "Downloading: $name.lrc"
    curl -sL -o "$LRC_DIR/$name.lrc" "$BASE_URL/$encoded.lrc"
  fi
done

echo "✅ Download complete!"
echo "Audio files: $(ls "$AUDIO_DIR"/*.mp3 2>/dev/null | wc -l)"
echo "LRC files: $(ls "$LRC_DIR"/*.lrc 2>/dev/null | wc -l)"
