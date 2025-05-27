"""
Module Loader Utility

This utility loads a module dynamically and executes its methods.

Module Requirements for Compatibility:
--------------------------------------
1. Each module must define a 'run' function at the module level that serves as the default entry point
2. Modules can also define additional functions for specific commands (e.g., 'list', 'scan_data')
3. All functions must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
4. All functions should return a dictionary with results
5. The module typically defines a manager class to encapsulate module-specific functionality
6. The module should maintain a singleton instance of the manager for efficiency

Example of a compatible module:
------------------------------
```python
def run(subscription_id=None, resource_group=None, **kwargs):
    # Default entry point - Initialize resources and perform default operation
    return {"result": "success", "data": [...]}

def list(subscription_id=None, resource_group=None, **kwargs):
    # List command implementation
    return {"result": "success", "data": [...]}

def scan_data(subscription_id=None, resource_group=None, **kwargs):
    # Scan data command implementation
    return {"result": "success", "data": [...]}
```
"""

import importlib
import logging
from typing import Any, Dict, Optional

log = logging.getLogger("fabric_friend")

def load_and_run(module_name: str, args: Optional[Dict[str, Any]] = None, command: Optional[str] = None) -> Any:
    """
    Dynamically load a module and execute its specified command or default run method.
    
    This function expects modules to follow a standard format:
    1. The module must have a top-level 'run' function as the default entry point
    2. The module can have additional functions for specific commands
    3. All functions must accept the parameters provided in args
    4. All functions should return a dictionary with results
    
    When creating new modules, ensure they follow this structure to be compatible
    with this loader utility.
    
    Args:
        module_name: The name of the module to load (e.g., 'modules.fabric')
        args: Optional dictionary of arguments to pass to the function
        command: Optional command name to execute (if None, runs the default 'run' function)
        
    Returns:
        The result of the module's function
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the module does not have the requested function
    """
    try:
        # Default empty args if none provided
        if args is None:
            args = {}
            
        log.info(f"Loading module: {module_name}")
        
        # Import the module dynamically
        module = importlib.import_module(module_name)
        
        # Determine which function to call
        func_name = command if command else "run"
        
        # If the specific command function doesn't exist, fall back to the default 'run' function
        if command and not hasattr(module, func_name):
            log.warning(f"Module {module_name} does not have a {func_name} function, falling back to 'run'")
            func_name = "run"
        
        # At this point, the module MUST have at least the 'run' function
        if not hasattr(module, func_name):
            log.error(f"Module {module_name} does not have a {func_name} function")
            raise AttributeError(f"Module {module_name} does not have a {func_name} function")
        
        # Get the function to execute
        func = getattr(module, func_name)
        
        # Execute the function with the provided arguments, passing command if using 'run'
        log.info(f"Executing {module_name}.{func_name}()")
        if func_name == "run" and command:
            # If we're using the default run function with a specific command, pass the command name
            args_with_command = args.copy()
            args_with_command["command"] = command
            return func(**args_with_command)
        else:
            return func(**args)
        
    except ImportError as e:
        log.error(f"Failed to import module {module_name}: {str(e)}")
        raise
    except Exception as e:
        # Use the most recently used func_name or a default value if we didn't get that far
        current_func = locals().get("func_name", "unknown")
        log.error(f"Error executing {current_func} in {module_name}: {str(e)}")
        raise
