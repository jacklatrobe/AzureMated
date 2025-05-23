"""
Template Module

This template provides a starting point for creating new modules that are compatible
with the module_loader utility.

Module Structure for Module Loader Compatibility:
-------------------------------------------------
1. Each module must define a 'run' function at the module level that serves as the default entry point
2. Modules can define additional functions for specific commands (e.g., 'list', 'scan_data')
3. All functions must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
4. All functions should return a dictionary with results
5. The module typically defines a manager class to encapsulate module-specific functionality
6. The module should maintain a singleton instance of the manager for efficiency

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
        Example operation function (default).
        
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
    
    def list_items(self, resource_group=None):
        """
        Example list operation.
        
        Args:
            resource_group: Optional resource group to filter by
            
        Returns:
            Dictionary containing list results
        """
        log.info(f"Listing items for subscription {self.subscription_id}")
        if resource_group:
            log.info(f"Filtering by resource group: {resource_group}")
        
        # Implement your list functionality here
        return {
            "status": "success",
            "items": [
                {"id": "item1", "name": "Example Item 1"},
                {"id": "item2", "name": "Example Item 2"}
            ]
        }
    
    def scan_data(self, item_id=None):
        """
        Example scan data operation.
        
        Args:
            item_id: Optional ID of the item to scan
            
        Returns:
            Dictionary containing scan results
        """
        log.info(f"Scanning data for subscription {self.subscription_id}")
        if item_id:
            log.info(f"Scanning specific item: {item_id}")
        
        # Implement your scan data functionality here
        return {
            "status": "success",
            "scan_results": {
                "total_items": 10,
                "scanned_items": 10,
                "findings": []
            }
        }

# Create a manager instance
_template_manager = None

def run(subscription_id=None, param1=None, param2=None, **kwargs):
    """
    Run the Template module functionality (default entry point).
    
    This function is called by the module_loader when no specific command is provided.
    
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
    
    log.info("Running Template module default operation")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the manager
    if _template_manager is None or _template_manager.subscription_id != subscription_id:
        _template_manager = TemplateManager(credential, subscription_id)
    
    # Perform the default operation
    return _template_manager.example_operation(param1, param2)

def list(subscription_id=None, resource_group=None, **kwargs):
    """
    List items in the Template module.
    
    This function is called by the module_loader when the 'list' command is specified.
    
    Args:
        subscription_id: The Azure subscription ID
        resource_group: Optional resource group to filter by
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with the list results
    """
    from utils import initialize_credential
    
    global _template_manager
    
    log.info("Running Template module list command")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the manager
    if _template_manager is None or _template_manager.subscription_id != subscription_id:
        _template_manager = TemplateManager(credential, subscription_id)
    
    # Perform the list operation
    return _template_manager.list_items(resource_group)

def scan_data(subscription_id=None, item_id=None, **kwargs):
    """
    Scan data in the Template module.
    
    This function is called by the module_loader when the 'scan-data' command is specified.
    
    Args:
        subscription_id: The Azure subscription ID
        item_id: Optional ID of the item to scan
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with the scan results
    """
    from utils import initialize_credential
    
    global _template_manager
    
    log.info("Running Template module scan-data command")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the manager
    if _template_manager is None or _template_manager.subscription_id != subscription_id:
        _template_manager = TemplateManager(credential, subscription_id)
    
    # Perform the scan operation
    return _template_manager.scan_data(item_id)
