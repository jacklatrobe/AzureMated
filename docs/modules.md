# Module System

FabricFriend uses a dynamic module system to organize functionality and enable easy extension.

## Overview

The module system allows specialized functionality to be encapsulated in separate modules that can be loaded and executed at runtime. This provides several benefits:

- **Separation of concerns**: Each module focuses on a specific domain
- **Extensibility**: New functionality can be added without modifying existing code
- **Maintainability**: Code is organized into logical units
- **Reusability**: Modules can be reused across different commands

## Module Structure

Each module follows a standardized structure to ensure compatibility with the module loader:

```
modules/
└── example_module.py
```

### Required Components

1. **Manager Class**
   - Encapsulates module-specific functionality
   - Accepts `credential` and `subscription_id` in constructor
   - Implements methods for operations in the module's domain

2. **Singleton Instance**
   - Maintained at the module level
   - Allows efficient reuse of the manager

3. **Run Function**
   - Defined at the module level (not inside a class)
   - Serves as the entry point for the module
   - Accepts standard parameters (`subscription_id` and `**kwargs`)
   - Returns a dictionary with results

## Module Interface

All modules must implement this standard interface:

```python
def run(subscription_id=None, **kwargs):
    """
    Module entry point.
    
    Args:
        subscription_id: The Azure subscription ID
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with results
    """
    # Initialize resources
    # Perform operations
    return {"result": "success", "data": [...]}
```

## Module Loading

Modules are loaded dynamically using the `module_loader` utility:

```python
from utils import load_and_run

# Load and run a module
result = load_and_run("modules.example_module", {
    "subscription_id": "00000000-0000-0000-0000-000000000000",
    "param1": "value1"
})
```

## Available Modules

FabricFriend includes these built-in modules:

- **fabric.py**: Operations related to Microsoft Fabric instances
- **powerbi.py**: Operations related to Power BI Premium instances
- **azure_topology.py**: Visualization of Azure resource topology

## Creating New Modules

To create a new module:

1. Create a new Python file in the `modules` directory
2. Follow the standard module structure (see [Templates](templates.md))
3. Implement the manager class with appropriate methods
4. Define the `run` function
5. Update the `modules/__init__.py` file to import the new module

See the [Templates](templates.md) documentation for a starter template.

## Best Practices

- Keep modules focused on a specific domain
- Follow the standard structure for compatibility
- Include comprehensive documentation
- Implement robust error handling
- Return consistent result structures
- Maintain backward compatibility

## See Also

- [Architecture Overview](architecture.md)
- [Utilities](utilities.md)
- [Templates](templates.md)
