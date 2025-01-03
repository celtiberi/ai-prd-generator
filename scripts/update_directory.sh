#!/bin/bash

# Configuration
PROJECT_ROOT="."
OUTPUT_FILE=".notes/directory_structure.md"
CURSOR_IGNORE=".cursorignore"

# Function to check if path should be ignored
should_ignore() {
    local path=$1
    
    # Read patterns from .cursorignore
    while IFS= read -r pattern; do
        # Skip comments and empty lines
        [[ $pattern =~ ^#.*$ ]] && continue
        [[ -z $pattern ]] && continue
        
        if [[ "$path" == *"$pattern"* ]]; then
            return 0
        fi
    done < "$CURSOR_IGNORE"
    
    return 1
}

# Function to generate directory structure
generate_structure() {
    local base=$1
    local prefix=$2
    
    # List directories first, then files (including hidden ones)
    for entry in "$base"/.* "$base"/*; do
        # Skip . and .. directory entries
        [[ "${entry##*/}" == "." || "${entry##*/}" == ".." ]] && continue
        
        [[ -e "$entry" ]] || continue
        
        local path=${entry#./}
        should_ignore "$path" && continue
        
        if [ -d "$entry" ]; then
            echo "${prefix}${path}/"
            generate_structure "$entry" "$prefix  "
        else
            echo "${prefix}${path}"
        fi
    done
}

# Generate markdown content
generate_markdown() {
    cat << EOF
# Project Directory Structure

\`\`\`tree
$(generate_structure "$PROJECT_ROOT" "")
\`\`\`
EOF
}

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Generate and save the markdown
generate_markdown > "$OUTPUT_FILE"

echo "Directory structure updated in $OUTPUT_FILE" >&2 