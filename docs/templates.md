# Templates

FabricFriend includes templates to help you create new modules and extensions.

## Module Template

The module template provides a starting point for creating new modules that are compatible with the module loader system.

### Template Structure

```python
"""
[Service Name] Module

This module contains functions for interacting with [Azure Service Name].

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

class ServiceManager:
    """
    Class for managing [Azure Service Name] resources.
    
    This manager encapsulates all operations related to the Azure service,
    including listing, getting, creating, and managing service resources.
    """
    
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        """
        Initialize the ServiceManager.
        
        Args:
            credential: The Azure credential for authentication
            subscription_id: The Azure subscription ID
        """
        self.credential = credential
        self.subscription_id = subscription_id
        
        # TODO: Initialize Azure SDK client for your service
        # Example:
        # from azure.mgmt.yourservice import YourServiceManagementClient
        # self.client = YourServiceManagementClient(credential, subscription_id)
        
    def list_resources(self, resource_group=None):
        """
        List all service resources in the subscription.
        
        Args:
            resource_group: Optional resource group to filter by
            
        Returns:
            List of service resources
        """
        log.info(f"Listing {self.__class__.__name__.replace('Manager', '')} resources")
        
        # TODO: Implement service resource listing using Azure SDK
        # Example:
        # try:
        #     if resource_group:
        #         resources = self.client.resources.list_by_resource_group(resource_group)
        #     else:
        #         resources = self.client.resources.list()
        #     return [resource.as_dict() for resource in resources]
        # except AzureError as e:
        #     log.error(f"Error listing resources: {str(e)}")
        #     raise
        
        # Placeholder implementation
        return []
        
    def get_resource(self, resource_id):
        """
        Get details for a specific service resource.
        
        Args:
            resource_id: The ID of the service resource
            
        Returns:
            Details of the service resource
        """
        log.info(f"Getting resource details for {resource_id}")
        
        # TODO: Implement service resource retrieval using Azure SDK
        # Example:
        # try:
        #     resource = self.client.resources.get(resource_id)
        #     return resource.as_dict()
        # except AzureError as e:
        #     log.error(f"Error getting resource {resource_id}: {str(e)}")
        #     raise
        
        # Placeholder implementation
        return {}
    
    def create_resource(self, resource_name, resource_group, **properties):
        """
        Create a new service resource.
        
        Args:
            resource_name: Name for the new resource
            resource_group: Resource group for the new resource
            **properties: Additional properties for resource creation
            
        Returns:
            Details of the created resource
        """
        log.info(f"Creating resource {resource_name} in {resource_group}")
        
        # TODO: Implement resource creation using Azure SDK
        # This is optional - not all modules need create operations
        
        # Placeholder implementation
        return {}

# Create a service manager instance (singleton pattern)
_service_manager = None

def run(subscription_id=None, resource_group=None, resource_id=None, **kwargs):
    """
    Run the Service module functionality.
    
    This function is called by the module_loader and serves as the entry point
    for this module. The module_loader expects this function to exist in all modules
    and will call it with parameters parsed from command line arguments or API calls.
    
    Args:
        subscription_id: The Azure subscription ID (required)
        resource_group: Optional resource group to filter by
        resource_id: Optional specific resource ID to retrieve
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
    
    global _service_manager
    
    log.info("Running Service module")
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the service manager
    if _service_manager is None or _service_manager.subscription_id != subscription_id:
        _service_manager = ServiceManager(credential, subscription_id)
    
    # Determine the operation to perform based on parameters
    if resource_id:
        # Get a specific resource
        return {"resource": _service_manager.get_resource(resource_id)}
    else:
        # List resources
        return {"resources": _service_manager.list_resources(resource_group)}

# Optional: Implement specific command functions
def list(subscription_id=None, resource_group=None, **kwargs):
    """
    List service resources.
    
    This function is called when the user runs: python main.py service list
    
    Args:
        subscription_id: The Azure subscription ID
        resource_group: Optional resource group to filter by
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with list of resources
    """
    from utils import initialize_credential
    
    global _service_manager
    
    log.info("Running Service list command")
    
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    credential = initialize_credential()
    
    if _service_manager is None or _service_manager.subscription_id != subscription_id:
        _service_manager = ServiceManager(credential, subscription_id)
    
    return {"resources": _service_manager.list_resources(resource_group)}

def get(subscription_id=None, resource_id=None, **kwargs):
    """
    Get specific service resource.
    
    This function is called when the user runs: python main.py service get
    
    Args:
        subscription_id: The Azure subscription ID
        resource_id: The ID of the resource to retrieve
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with resource details
    """
    from utils import initialize_credential
    
    global _service_manager
    
    log.info("Running Service get command")
    
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    if not resource_id:
        raise ValueError("Resource ID is required")
    
    credential = initialize_credential()
    
    if _service_manager is None or _service_manager.subscription_id != subscription_id:
        _service_manager = ServiceManager(credential, subscription_id)
    
    return {"resource": _service_manager.get_resource(resource_id)}
```
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
```

### Usage

To create a new module using the template:

1. **Create Module File**
   ```powershell
   # Copy template to new file
   Copy-Item "docs\templates.md" "modules\your_service.py"
   ```

2. **Customize the Template**
   - Replace `[Service Name]` and `[Azure Service Name]` with your service details
   - Rename `ServiceManager` to `YourServiceManager`
   - Update method names to match your service operations
   - Implement Azure SDK integration

3. **Install Dependencies**
   Add required Azure SDK packages to `requirements.txt`:
   ```
   azure-mgmt-yourservice>=1.0.0
   ```

4. **Update Module Package**
   Add import to `modules/__init__.py`:
   ```python
   from .your_service import YourServiceManager
   ```

5. **Add CLI Integration**
   Update `main.py` to add CLI commands for your module (see example in main.py)

6. **Test Implementation**
   Create unit tests following the pattern in `tests/` directory

## Customization

### Required Customizations

1. **Service-Specific Manager Class**
   ```python
   class FabricManager:  # Replace with your service
       def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
           from azure.mgmt.fabric import FabricManagementClient  # Your SDK
           self.client = FabricManagementClient(credential, subscription_id)
   ```

2. **Service Operations**
   ```python
   def list_instances(self, resource_group=None):  # Rename appropriately
       """List Fabric instances"""  # Update description
       # Implement using your Azure SDK client
   ```

3. **Return Data Structures**
   ```python
   # Use consistent naming for your service
   return {"instances": [...]}      # For Fabric instances
   return {"workspaces": [...]}     # For workspace resources  
   return {"databases": [...]}      # For database resources
   ```

### Optional Customizations

1. **Additional Command Functions**
   ```python
   def scan_data(subscription_id=None, **kwargs):
       """Custom operation specific to your service"""
       pass
   
   def backup(subscription_id=None, resource_id=None, **kwargs):
       """Service-specific backup operation"""
       pass
   ```

2. **Service-Specific Parameters**
   ```python
   def run(subscription_id=None, workspace_id=None, database_name=None, **kwargs):
       """Add parameters specific to your service"""
       pass
   ```

3. **Error Handling**
   ```python
   from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
   
   try:
       result = self.client.operation()
   except ResourceNotFoundError:
       log.warning(f"Resource not found: {resource_id}")
       return {"error": "Resource not found"}
   except ClientAuthenticationError:
       log.error("Authentication failed")
       raise
   ```

### Implementation Checklist

- [ ] Replace template placeholders with service-specific names
- [ ] Install and import appropriate Azure SDK packages
- [ ] Implement manager class with service operations
- [ ] Add required `run()` function following standard pattern
- [ ] Add optional command functions for specific operations
- [ ] Update `modules/__init__.py` with new manager import
- [ ] Add CLI command definitions in `main.py`
- [ ] Create unit tests for module loading and basic operations
- [ ] Update `requirements.txt` with new dependencies
- [ ] Test module through CLI and programmatic interfaces
- [ ] Document any service-specific parameters or behaviors

## See Also

- [Module System](modules.md)
- [Architecture Overview](architecture.md)
