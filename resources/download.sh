#!/bin/bash
# Download NCE Book 1 audio & LRC from wychl/nce GitHub repo
# Source: https://github.com/wychl/nce
# Audio: US English version, paired files (1&2, 3&4, etc.)
# LRC: Synchronized lyrics with sentence timestamps

cd "$(dirname "$0")"
BASE_URL="https://raw.githubusercontent.com/wychl/nce/main/us/NCE1"
AUDIO_DIR="audio"
LRC_DIR="lrc"

mkdir -p "$AUDIO_DIR" "$LRC_DIR"

# Paired files for all 144 lessons of Book 1
declare -A FILES
FILES["001&002.Excuse Me"]=""
FILES["003&004.Sorry, Sir"]=""
FILES["005&006.Nice to Meet You"]=""
FILES["007&008.Are You a Teacher"]=""
FILES["009&010.How Are You Today"]=""
FILES["011&012.Is This Your Shirt"]=""
FILES["013&014.A New Dress"]=""
FILES["015&016.Your Passports, Please"]=""
FILES["017&018.How Do You Do"]=""
FILES["019&020.Tired and Thirsty"]=""
FILES["021&022.What Colour Is It"]=""
FILES["023&024.Which Glasses"]=""
FILES["025&026.Mrs. Smith's Kitchen"]=""
FILES["027&028.A Nice Room"]=""
FILES["029&030.Come In"]=""
FILES["031&032.Where's Sally"]=""
FILES["033&034.A Fine Day"]=""
FILES["035&036.Our Village"]=""
FILES["037&038.Making a Bookcase"]=""
FILES["039&040.Don't Drop It"]=""
FILES["041&042.Penny's Bag"]=""
FILES["043&044.Hurry Up"]=""
FILES["045&046.The Boss's Letter"]=""
FILES["047&048.A Cup of Tea"]=""
FILES["049&050.At the Butcher's"]=""
FILES["051&052.A Pleasant Climate"]=""
FILES["053&054.An Interesting Game"]=""
FILES["055&056.The Sawyer Family"]=""
FILES["057&058.An Unusual Day"]=""
FILES["059&060.Is That All"]=""
FILES["061&062.A Bad Cold"]=""
FILES["063&064.Not a Bad Cold"]=""
FILES["065&066.Not a Baby"]=""
FILES["067&068.The Weekend"]=""
FILES["069&070.Car Race"]=""
FILES["071&072.He's Awful"]=""
FILES["073&074.A Nice Garden"]=""
FILES["075&076.Uncomfortable Shoes"]=""
FILES["077&078.Terrible Toothache"]=""
FILES["079&080.Carol's Shopping List"]=""
FILES["081&082.Roast Beef and Potatoes"]=""
FILES["083&084.Having a Meal"]=""
FILES["085&086.Paris in the Spring"]=""
FILES["087&088.A Car Crash"]=""
FILES["089&090.For Yourself"]=""
FILES["091&092.Poor Ian"]=""
FILES["093&094.Our New Neighbour"]=""
FILES["095&096.Tickets Please"]=""
FILES["097&098.A Small Blue Case"]=""
FILES["099&100.Ow!"]=""
FILES["101&102.A Card from Jimmy"]=""
FILES["103&104.The French Test"]=""
FILES["105&106.Full of Mistakes"]=""
FILES["107&108.Too Small"]=""
FILES["109&110.A Good Idea"]=""
FILES["111&112.The Most Expensive Model"]=""
FILES["113&114.Small Change"]=""
FILES["115&116.Knock Knock"]=""
FILES["117&118.A Real Shock"]=""
FILES["119&120.A Telephone Call"]=""
FILES["121&122.The Man in the Hat"]=""
FILES["123&124.A Trip to the Moon"]=""
FILES["125&126.Tea for Two"]=""
FILES["127&128.A Famous Actress"]=""
FILES["129&130.Seven-Fifty"]=""
FILES["131&132.Don't Be Late"]=""
FILES["133&134.Guess What"]=""
FILES["135&136.The Latest Report"]=""
FILES["137&138.A Greedy Young Man"]=""
FILES["139&140.Is That You John"]=""
FILES["141&142.A Nervous Flight"]=""
FILES["143&144.A Walk Through the Woods"]=""

downloaded=0
skipped=0

for name in "${!FILES[@]}"; do
  # URL encode
  encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$name'))")
  
  # Download MP3
  if [ ! -f "$AUDIO_DIR/$name.mp3" ] || [ ! -s "$AUDIO_DIR/$name.mp3" ]; then
    echo "📥 $name.mp3"
    curl -sL -o "$AUDIO_DIR/$name.mp3" "$BASE_URL/$encoded.mp3"
    if [ -s "$AUDIO_DIR/$name.mp3" ]; then
      downloaded=$((downloaded + 1))
    else
      rm -f "$AUDIO_DIR/$name.mp3"
      echo "  ❌ Failed"
    fi
  else
    skipped=$((skipped + 1))
  fi
  
  # Download LRC
  if [ ! -f "$LRC_DIR/$name.lrc" ] || [ ! -s "$LRC_DIR/$name.lrc" ]; then
    curl -sL -o "$LRC_DIR/$name.lrc" "$BASE_URL/$encoded.lrc"
  fi
done

echo ""
echo "✅ Done! Downloaded: $downloaded | Skipped (exists): $skipped"
echo "   Audio: $(ls "$AUDIO_DIR"/*.mp3 2>/dev/null | wc -l) files"
echo "   LRC:   $(ls "$LRC_DIR"/*.lrc 2>/dev/null | wc -l) files"
