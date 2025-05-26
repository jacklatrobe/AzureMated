# FabricFriend Architecture

FabricFriend is built with a modular, extensible architecture designed to support a wide range of Azure management operations.

## High-Level Architecture

```
┌─────────────────┐
│   CLI Parser    │ (main.py)
└─────────────────┘
        │
        ▼
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Main Program   │────▶│ Module Loader │────▶│ Cloud Modules   │
│  (main.py)      │     │ (module_loader)│    │ (fabric, powerbi│
└─────────────────┘     └───────────────┘     │ azure_topology) │
        │                       │              └─────────────────┘
        │                       │                      │
        ▼                       ▼                      ▼
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Utilities      │     │  Auth Utils   │     │ Azure SDK APIs  │
│  (common.py)    │     │  (auth.py)    │     │ (Management,    │
└─────────────────┘     └───────────────┘     │  Fabric, etc.)  │
                                               └─────────────────┘
```

## Components

### Main Program (`main.py`)

The entry point of the application that:
- Parses command-line arguments using argparse with subparsers for each module
- Implements a Docker-like CLI structure: `fabricfriend [module] [command] [arguments]`
- Routes commands to the `run_module()` function which uses the module loader
- Provides built-in functions for authentication checking
- Uses Rich console for formatted output

**Key Functions:**
- `run_module(args)`: Routes module execution through the module loader
- `check_auth(args)`: Validates Azure and Microsoft 365 authentication
- `main()`: CLI argument parsing and command routing

### Module System

A dynamic loading system that allows cloud service-specific functionality to be organized into modules:

**Module Loader (`utils/module_loader.py`)**
- `load_and_run(module_name, args, command)`: Core function for dynamic module execution
- Supports both default `run` function and specific command functions (e.g., `list`, `get`)
- Handles module importing, function resolution, and error handling
- Expects modules to follow standard interface patterns

**Module Structure Requirements:**
1. **Manager Class**: Encapsulates cloud service-specific functionality
2. **Global Singleton**: Module-level manager instance for efficiency
3. **Run Function**: Standard entry point accepting `subscription_id` and `**kwargs`
4. **Command Functions**: Optional specific command implementations
5. **Standard Return Format**: Dictionary with results

### Utilities

**Authentication (`utils/auth.py`)**
- `initialize_credential()`: Creates ChainedTokenCredential with Azure CLI and Azure Developer CLI
- `check_azure_auth()`: Validates Azure authentication status
- Automatic credential testing and fallback

**Display (`utils/common.py`)**
- `console`: Rich console instance for styled output
- `format_table()`: Creates Rich tables from data dictionaries
- `display_results()`: Displays formatted tables or "no data" messages

**Module Loading (`utils/module_loader.py`)**
- Dynamic module importing and execution
- Support for default and named command functions
- Comprehensive error handling and logging

### Cloud Service Integration

Integration with Azure services through the Azure Python SDK:

**Supported Services:**
- **Microsoft Fabric**: `azure-mgmt-fabric` SDK (modules/fabric.py)
- **Power BI**: Power BI Admin REST API (No SDK) (modules/powerbi.py)  
- **Azure Resources**: `azure-mgmt-resource` SDK (modules/azure_topology.py)

**Integration Pattern:**
- Each module defines a Manager class that wraps Azure SDK clients
- Credential injection through constructor
- Consistent method naming and return formats
- Error handling with Azure-specific exceptions

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

1. **CLI Parsing**: User executes command like `python main.py fabric list -s <subscription_id>`
2. **Argument Parsing**: Main program uses argparse subparsers to parse module and command
3. **Module Routing**: `run_module()` function prepares arguments and calls module loader
4. **Dynamic Loading**: Module loader imports the specified module (e.g., `modules.fabric`)
5. **Function Resolution**: Loader determines whether to call `run()` or specific command function
6. **Authentication**: Module initializes credentials using `initialize_credential()`
7. **Manager Initialization**: Module creates or reuses Manager class singleton
8. **Operation Execution**: Manager performs Azure SDK operations
9. **Result Formatting**: Results returned as dictionary and displayed via Rich console

**Example Flow for `python main.py fabric list -s sub123`:**
```
main.py → run_module() → load_and_run("modules.fabric", args, "list") 
→ fabric.list() → FabricManager.list_instances() → Azure SDK call → results
```

**Module Command Support:**
- Default: `run()` function (required)
- Optional: Command-specific functions (`list()`, `get()`, `scan_data()`, etc.)
- Fallback: If command function doesn't exist, calls `run()` with command parameter

## See Also

- [Module System](modules.md)
- [Utilities](utilities.md)
- [Authentication](authentication.md)
