#!/bin/bash
# Download NCE Book 1 audio from GitHub (wychl/nce - US version)
# Audio files are paired: 001&002, 003&004, etc.

BASE_URL="https://raw.githubusercontent.com/wychl/nce/main/us/NCE1"
AUDIO_DIR="audio"

mkdir -p "$AUDIO_DIR"

# Pairs: 1&2, 3&4, 5&6, ..., 19&20 (for our L1-L20)
pairs=(
  "001&002.Excuse Me"
  "003&004.Sorry, Sir"
  "005&006.Nice to Meet You"
  "007&008.Are You a Teacher"
  "009&010.Look at"
  "011&012.Is this your shirt"
  "013&014.A new dress"
  "015&016.Your passports, please"
  "017&018.How do you do"
  "019&020.Big and small"
)

for pair in "${pairs[@]}"; do
  filename="${pair}.mp3"
  echo "Downloading: $filename"
  # URL encode the & as %26 and spaces as %20
  url_filename=$(echo "$filename" | sed 's/&/%26/g' | sed 's/ /%20/g')
  curl -sL -o "$AUDIO_DIR/$filename" "$BASE_URL/$url_filename"
  if [ -f "$AUDIO_DIR/$filename" ] && [ -s "$AUDIO_DIR/$filename" ]; then
    echo "  ✓ Downloaded ($(( $(wc -c < "$AUDIO_DIR/$filename") / 1024 ))KB)"
  else
    echo "  ✗ Failed"
  fi
done

echo ""
echo "Download complete!"
ls -lh "$AUDIO_DIR"/*.mp3 2>/dev/null
