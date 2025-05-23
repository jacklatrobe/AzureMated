"""
Module Loader Utility

This utility loads a module dynamically and executes its run method.

Module Requirements for Compatibility:
--------------------------------------
1. Each module must define a 'run' function at the module level that serves as the entry point
2. The 'run' function must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
3. The 'run' function should return a dictionary with results
4. The module typically defines a manager class to encapsulate module-specific functionality
5. The module should maintain a singleton instance of the manager for efficiency

Example of a compatible module:
------------------------------
```python
def run(subscription_id=None, resource_group=None, **kwargs):
    # Initialize resources
    # Perform operations
    return {"result": "success", "data": [...]}
```
"""

import importlib
import logging
from typing import Any, Dict, Optional

log = logging.getLogger("fabric_friend")

def load_and_run(module_name: str, args: Optional[Dict[str, Any]] = None) -> Any:
    """
    Dynamically load a module and execute its run method.
    
    This function expects modules to follow a standard format:
    1. The module must have a top-level 'run' function
    2. The 'run' function must accept the parameters provided in args
    3. The 'run' function should return a dictionary with results
    
    When creating new modules, ensure they follow this structure to be compatible
    with this loader utility.
    
    Args:
        module_name: The name of the module to load (e.g., 'modules.fabric')
        args: Optional dictionary of arguments to pass to the run method
        
    Returns:
        The result of the module's run method
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the module does not have a run method
    """
    try:
        # Default empty args if none provided
        if args is None:
            args = {}
            
        log.info(f"Loading module: {module_name}")
        
        # Import the module dynamically
        module = importlib.import_module(module_name)
        
        # Check if the module has a run method
        if not hasattr(module, "run"):
            log.error(f"Module {module_name} does not have a run method")
            raise AttributeError(f"Module {module_name} does not have a run method")
        
        # Execute the run method with the provided arguments
        log.info(f"Executing {module_name}.run()")
        return module.run(**args)
        
    except ImportError as e:
        log.error(f"Failed to import module {module_name}: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Error executing run method in {module_name}: {str(e)}")
        raise
