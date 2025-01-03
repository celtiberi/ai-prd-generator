# Development Guidelines

This document outlines development standards and practices for the AI PRD Generator project. Guidelines are provided in YAML format for AI parsing while maintaining human readability.

```yaml
development_standards:
  code_style:
    python:
      style_guide: PEP 8
      type_hints: required
      docstrings:
        format: Google style
        required_for:
          - classes
          - methods
          - functions
```

## Quick Reference

1. **Python Standards**
   - Use type hints
   - Google-style docstrings
   - Custom exceptions for domain errors
   - Pydantic for validation

2. **TypeScript Standards**
   - Strict type checking
   - Functional components
   - Props interfaces required
   - Error boundaries for components

3. **Git Practices**
   - Conventional commits
   - Feature branch workflow
   - Clear branch naming 