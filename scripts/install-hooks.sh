#!/bin/bash

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Update directory structure
./scripts/update_directory.sh

# Add the updated file to the commit if it changed
git add .notes/directory_structure.md
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit 