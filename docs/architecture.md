# FabricFriend Architecture

FabricFriend is built with a modular, extensible architecture designed to support a wide range of Azure management operations.

## High-Level Architecture

```
┌────────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Main Program  │────▶│ Module Loader │────▶│ Module Handlers │
└────────────────┘     └───────────────┘     └─────────────────┘
        │                                            │
        │                                            │
        ▼                                            ▼
┌────────────────┐                         ┌─────────────────┐
│  Utilities     │◀────────────────────────│ Azure Services  │
└────────────────┘                         └─────────────────┘
```

## Components

### Main Program (`main.py`)

The entry point of the application that:
- Parses command-line arguments
- Routes commands to appropriate handlers
- Provides high-level functions for common operations

### Module System

A dynamic loading system that allows specialized functionality to be organized into modules:
- Each module is a Python file in the `modules` directory
- Modules follow a standardized structure for compatibility
- The module loader dynamically loads and executes modules based on user commands

### Utilities

Common functionality shared across the application:
- Authentication helpers
- Display formatters
- Module loading utilities

### Azure Service Integration

Integration with various Azure services through the Azure Python SDK:
- Microsoft Fabric API
- Power BI API
- Azure Resource Management API

## Directory Structure

```
FabricFriend/
├── main.py                  # Main entry point
├── requirements.txt         # Dependencies
├── docs/                    # Documentation
├── modules/                 # Module files
│   ├── __init__.py
│   ├── fabric.py
│   ├── powerbi.py
│   └── azure_topology.py
└── utils/                   # Utility functions
    ├── __init__.py
    ├── auth.py
    ├── common.py
    └── module_loader.py
```

## Program Flow

1. User executes a command through the CLI
2. Main program parses arguments and determines the requested operation
3. For standard operations, the main program calls the appropriate function
4. For module-based operations, the module loader dynamically loads and executes the specified module
5. The module executes the requested operation and returns results
6. Results are formatted and displayed to the user

## See Also

- [Module System](modules.md)
- [Utilities](utilities.md)
- [Authentication](authentication.md)
