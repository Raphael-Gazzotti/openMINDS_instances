#!/bin/bash

# Define the folder path and a list of strings to replace
folder_path="$1"
replacements=(
  "https://openminds.ebrains.eu/core/" "https://openminds.om-i.org/types/core/"
  "https://openminds.ebrains.eu/sands/" "https://openminds.om-i.org/types/sands/"
  "https://openminds.ebrains.eu/controlledTerms/" "https://openminds.om-i.org/types/controlledTerms/"
  "https://openminds.ebrains.eu/chemicals/" "https://openminds.om-i.org/types/chemicals/"
  "https://openminds.ebrains.eu/ephys/" "https://openminds.om-i.org/types/ephys/"
  "https://openminds.ebrains.eu/computation/" "https://openminds.om-i.org/types/computation/"
  "https://openminds.ebrains.eu/stimulation/" "https://openminds.om-i.org/types/stimulation/"
  "https://openminds.ebrains.eu/specimenPrep/" "https://openminds.om-i.org/types/specimenPrep/"
  "https://openminds.ebrains.eu/publications/" "https://openminds.om-i.org/types/publications/"
  "https://openminds.ebrains.eu/neuroimaging/" "https://openminds.om-i.org/types/neuroimaging/"
  "https://openminds.ebrains.eu/vocab/" "https://openminds.om-i.org/props/"
  "https://openminds.ebrains.eu/instances/" "https://openminds.om-i.org/instances/"
)

# Check if folder path is provided
if [ -z "$folder_path" ]; then
  echo "Error: Please specify a folder path as an argument."
  exit 1
fi

# Check if folder exists
if [ ! -d "$folder_path" ]; then
  echo "Error: Folder '$folder_path' does not exist."
  exit 1
fi

# Function to replace strings in a file
replace_strings() {
  local file="$1"
  echo "Processing file: $file"

  # Read the file content into a variable
  local content
  content=$(< "$file")

  # Perform the replacements
  for (( i=0; i<${#replacements[@]}; i+=2 )); do
    old_string="${replacements[$i]}"
    new_string="${replacements[$i+1]}"

    # Replace URLs in @id, @type, and other fields
    content=$(echo "$content" | sed "s|${old_string}|${new_string}|g")
  done

  # Write changes only if the file was modified
  echo "$content" > "$file"
  echo "Modified file: $file"
}

export -f replace_strings

# Maximum number of parallel jobs
max_jobs=4

# Function to manage parallel jobs
run_in_parallel() {
  while [ "$(jobs | wc -l)" -ge "$max_jobs" ]; do
    # Wait for any background job to finish if there are $max_jobs jobs running
    wait -n
  done

  # Call the replace function in the background
  replace_strings "$1" &
}

# Process all files in the folder
find "$folder_path" -type f ! -name "*.bak" | while read -r file; do
  run_in_parallel "$file"
done

# Wait for all background jobs to finish
wait

# Final output to confirm completion
echo "All parallel jobs complete!"


# Find all files in the folder and process them
#find "$folder_path" -type f | grep -v ".bak" | while read file; do
#  replace_strings "$file"
#done

