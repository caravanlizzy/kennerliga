#!/bin/bash

# Define a set of colors to cycle through
colors=(
  "#1976d2" # Quasar Default Blue
  "#263238" # Blue Grey 900 (Very Dark/Professional)
  "#455a64" # Blue Grey 700 (Current-ish)
  "#00796b" # Teal 700 (Latest applied)
  "#303f9f" # Indigo 700 (Classic Professional)
  "#c62828" # Red 800 (Bold)
  "#6a1b9a" # Purple 800 (Elegant/Creative)
  "#2e7d32" # Green 800 (Solid/Trustworthy)
  "#e65100" # Orange 900 (Energetic)
  "#1565c0" # Blue 800 (Strong Corporate)
  "#0097a7" # Cyan 700 (Fresh)
  "#5d4037" # Brown 700 (Earthly/Warm)
  "#37474f" # Blue Grey 800
  "#3949ab" # Indigo 600
  "#00897b" # Teal 600
  "#512da8" # Deep Purple 700
  "#c2185b" # Pink 700
  "#0288d1" # Light Blue 700
  "#f4511e" # Deep Orange 600
  "#212121" # Grey 900 (Near Black/Sophisticated)
)

FILE="src/css/quasar.variables.scss"

while true; do
  for color in "${colors[@]}"; do
    echo "Applying color: $color"
    sed -i "s/\$primary: #[0-9a-fA-F]\{6\};/\$primary: $color;/" "$FILE"
    sleep 5
  done
done
