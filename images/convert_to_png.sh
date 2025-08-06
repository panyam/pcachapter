
for f in *.svg; do
  echo "Converting $f to png"
  filename=$(basename "$f" .svg)
  pngfile="$filename.png"
  rsvg-convert "$f" -o "$pngfile"

  echo "Converting $f to jpeg"
  sips -s format jpeg "$pngfile" --out "$filename.jpeg" -s formatOptions 95 > /dev/null 2>&1
done
