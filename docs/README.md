# AzureMated Documentation

This directory contains comprehensive documentation for the AzureMated project.

## Table of Contents

1. [Getting Started](getting-started.md) - Installation and basic usage
2. [Architecture Overview](architecture.md) - System design and components
3. [Module System](modules.md) - Module structure and interface requirements
4. [Module Development Guide](module-development-guide.md) - Complete guide for creating new modules
5. [Templates](templates.md) - Code templates for new modules
6. [Utilities](utilities.md) - Common functionality and helper classes
7. [Authentication](authentication.md) - Azure authentication and credential management
8. [Visualization Utilities](visualiser.md) - Generating Azure topology diagrams

## Quick Start for Module Development

If you're building a new cloud service module:

1. Read the [Module Development Guide](module-development-guide.md) for the complete process
2. Use the [Templates](templates.md) for boilerplate code
3. Follow the [Module System](modules.md) requirements for compatibility
4. Reference existing modules in the `modules/` directory for examples

## Architecture Quick Reference

```
CLI Command → Main Program → Module Loader → Cloud Service Module → Azure SDK → Azure Service
```

Each cloud service (Fabric, Power BI, etc.) is implemented as a separate module with standardized interfaces.
