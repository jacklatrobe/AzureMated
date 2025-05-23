"""
Power BI Module

This module contains functions for interacting with Power BI Premium instances.

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

class PowerBIManager:
    """
    Class for managing Power BI Premium instances.
    """
    
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        """
        Initialize the PowerBIManager.
        
        Args:
            credential: The Azure credential
            subscription_id: The Azure subscription ID
        """
        self.credential = credential
        self.subscription_id = subscription_id
        
    def list_premium_instances(self, resource_group=None):
        """
        List all Power BI Premium instances in the subscription.
        
        Args:
            resource_group: Optional resource group to filter by
            
        Returns:
            List of Power BI Premium instances
        """
        # TODO: Implement Power BI Premium instance listing
        log.info("Listing Power BI Premium instances")
        
        # Placeholder for actual implementation
        return []
        
    def get_premium_instance(self, instance_id):
        """
        Get details for a specific Power BI Premium instance.
        
        Args:
            instance_id: The ID of the Power BI Premium instance
            
        Returns:
            Details of the Power BI Premium instance
        """
        # TODO: Implement Power BI Premium instance retrieval
        log.info(f"Getting Power BI Premium instance details for {instance_id}")
        
        # Placeholder for actual implementation        return {}

# Create a Power BI manager instance
_powerbi_manager = None

def run(subscription_id=None, resource_group=None, instance_id=None, **kwargs):
    """
    Run the Power BI module functionality.
    
    This function is called by the module_loader and serves as the entry point
    for this module. The module_loader expects this function to exist in all modules
    and will call it with parameters parsed from command line arguments or API calls.
    
    Module Loader Integration:
    - This function must be defined at the module level (not inside a class)
    - It must accept subscription_id as a parameter
    - It should accept **kwargs to handle any additional parameters
    - It must return a dictionary with the results
    
    Args:
        subscription_id: The Azure subscription ID
        resource_group: Optional resource group to filter by
        instance_id: Optional specific instance ID to retrieve
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with the results of the operation
    """
    from utils import initialize_credential
    
    global _powerbi_manager
    
    log.info("Running Power BI module")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the Power BI manager
    if _powerbi_manager is None or _powerbi_manager.subscription_id != subscription_id:
        _powerbi_manager = PowerBIManager(credential, subscription_id)
    
    # Determine the operation to perform
    if instance_id:
        # Get a specific instance
        return {"instance": _powerbi_manager.get_premium_instance(instance_id)}
    else:
        # List instances
        return {"instances": _powerbi_manager.list_premium_instances(resource_group)}
