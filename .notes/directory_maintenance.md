rules:
  directory_maintenance:
    description: Keep directory structure documentation in sync
    file: .notes/directory_structure.md
    dependencies_documentation:
      path: .notes/dependencies
      rules:
        - Documentation is immutable reference material
        - Never modify external dependency documentation
        - If documentation seems incorrect, implementation should be fixed
        - New documentation can be added but existing files are read-only
      examples:
        correct:
          - Reading documentation to understand API
          - Fixing implementation to match documentation
          - Adding new dependency documentation files
        incorrect:
          - Modifying existing dependency documentation
          - Updating docs to match incorrect implementation
          - Changing API documentation to fix errors
    automation:
      script: scripts/update_directory.sh
      triggers:
        - Pre-commit hook
        - Manual updates via ./scripts/update_directory.sh