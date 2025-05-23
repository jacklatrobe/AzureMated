"""
Template Module

This template provides a starting point for creating new modules that are compatible
with the module_loader utility.

Module Structure for Module Loader Compatibility:
-------------------------------------------------
1. Each module must define a 'run' function at the module level that serves as the entry point
2. The 'run' function must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
3. The 'run' function should return a dictionary with results
4. The module typically defines a manager class to encapsulate module-specific functionality
5. The module should maintain a singleton instance of the manager for efficiency

When creating new modules, follow this pattern to ensure compatibility with the module_loader.
"""

from azure.identity import ChainedTokenCredential
from azure.core.exceptions import AzureError
import logging

log = logging.getLogger("fabric_friend")

class TemplateManager:
    """
    Template class for new module functionality.
    
    Replace this with your module-specific manager class.
    """
    
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        """
        Initialize the TemplateManager.
        
        Args:
            credential: The Azure credential
            subscription_id: The Azure subscription ID
        """
        self.credential = credential
        self.subscription_id = subscription_id
    
    def example_operation(self, param1=None, param2=None):
        """
        Example operation function.
        
        Replace this with your module-specific operations.
        
        Args:
            param1: Example parameter 1
            param2: Example parameter 2
            
        Returns:
            Dictionary containing operation results
        """
        log.info(f"Performing example operation with {param1} and {param2}")
        
        # Implement your functionality here
        return {
            "status": "success",
            "data": {
                "param1": param1,
                "param2": param2
            }
        }

# Create a manager instance
_template_manager = None

def run(subscription_id=None, param1=None, param2=None, **kwargs):
    """
    Run the Template module functionality.
    
    This function is called by the module_loader and serves as the entry point
    for this module.
    
    Args:
        subscription_id: The Azure subscription ID
        param1: Example parameter 1
        param2: Example parameter 2
        **kwargs: Additional arguments
        
    Module Loader Integration:
    - This function must be defined at the module level (not inside a class)
    - It must accept subscription_id as a parameter
    - It should accept **kwargs to handle any additional parameters
    - It must return a dictionary with the results
        
    Returns:
        Dictionary with the results of the operation
    """
    from utils import initialize_credential
    
    global _template_manager
    
    log.info("Running Template module")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the manager
    if _template_manager is None or _template_manager.subscription_id != subscription_id:
        _template_manager = TemplateManager(credential, subscription_id)
    
    # Perform the operation
    return _template_manager.example_operation(param1, param2)
