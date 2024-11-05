#!/bin/bash

# Check if the variable is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <variable>"
  exit 1
fi

variable=$1

# Create the directory if it doesn't exist
mkdir -p "$variable/fixtures"

# Run the commands
./manage.py dumpdata "$variable" > "$variable/fixtures/new_data.json"
jq . "$variable/fixtures/new_data.json" > "$variable/fixtures/sample_data.json"

# Delete the new_data.json file
rm "$variable/fixtures/new_data.json"

echo "Data dumped and processed successfully."
