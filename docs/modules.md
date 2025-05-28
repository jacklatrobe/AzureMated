# Module System

AzureMated uses a dynamic module system to organize functionality and enable easy extension.

## Overview

The module system allows specialized functionality to be encapsulated in separate modules that can be loaded and executed at runtime. This provides several benefits:

- **Separation of concerns**: Each module focuses on a specific domain
- **Extensibility**: New functionality can be added without modifying existing code
- **Maintainability**: Code is organized into logical units
- **Reusability**: Modules can be reused across different commands

## Module Structure

Each module is a Python file in the `modules/` directory that follows this standardized structure:

```
modules/
├── __init__.py              # Package initialization, imports Manager classes
├── fabric.py               # Microsoft Fabric operations
├── powerbi.py              # Power BI Premium operations
├── azure_topology.py       # Azure resource topology mapping
└── [new_module].py         # Your new cloud service module
```

### Required Components

Every cloud service module must implement these components:

1. **Manager Class**
   ```python
   class ServiceManager:
       def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
           self.credential = credential
           self.subscription_id = subscription_id
       
       def list_instances(self, resource_group=None):
           # Implementation using Azure SDK
           pass
   ```

2. **Global Singleton Instance**
   ```python
   # Module-level singleton for efficiency
   _service_manager = None
   ```

3. **Required `run` Function**
   ```python
   def run(subscription_id=None, **kwargs):
       """
       Module entry point called by module_loader.
       Must be defined at module level (not in a class).
       """
       # Implementation
       return {"result": "success", "data": [...]}
   ```

4. **Optional Command Functions**
   ```python
   def list(subscription_id=None, resource_group=None, **kwargs):
       """Optional: Specific command implementation"""
       pass
   
   def get(subscription_id=None, instance_id=None, **kwargs):
       """Optional: Get specific resource details"""
       pass
   ```

## Module Interface

All modules must implement this standard interface:

```python
def run(subscription_id=None, **kwargs):
    """
    Required module entry point.
    
    Args:
        subscription_id: The Azure subscription ID (required)
        **kwargs: Additional parameters (varies by module and command)
        
    Returns:
        Dictionary with results in consistent format:
        {
            "instances": [...],      # For list operations
            "instance": {...},       # For get operations  
            "topology": {...},       # For topology operations
            "dependencies": [...],   # For dependency operations
            "result": "success",     # Status indicator
            "data": [...]           # Generic data container
        }
    """
    # Standard implementation pattern:
    from utils import initialize_credential
    
    global _module_manager
    
    # Validate required parameters
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    # Initialize credential and manager
    credential = initialize_credential()
    if _module_manager is None or _module_manager.subscription_id != subscription_id:
        _module_manager = ModuleManager(credential, subscription_id)
    
    # Perform operation and return results
    return {"result": "success", "data": _module_manager.operation()}
```

### Optional Command Functions

Modules can implement specific command functions that override the default `run` behavior:

```python
def list(subscription_id=None, resource_group=None, **kwargs):
    """List resources - called when user runs 'module list'"""
    # Implementation
    return {"instances": [...]}

def get(subscription_id=None, instance_id=None, **kwargs):
    """Get specific resource - called when user runs 'module get'"""
    # Implementation  
    return {"instance": {...}}

def scan_data(subscription_id=None, **kwargs):
    """Custom command - called when user runs 'module scan-data'"""
    # Implementation
    return {"scanned_data": [...]}
```

**Command Resolution Order:**
1. If command-specific function exists (e.g., `list()`), call it
2. Otherwise, call `run()` function with command parameter in kwargs
3. Module determines operation based on parameters

## Module Loading

The module loader (`utils/module_loader.py`) provides dynamic module execution:

```python
from utils import load_and_run

# Load and run a module with default command
result = load_and_run("modules.fabric", {
    "subscription_id": "00000000-0000-0000-0000-000000000000",
    "resource_group": "my-resource-group"
})

# Load and run a module with specific command
result = load_and_run("modules.fabric", {
    "subscription_id": "00000000-0000-0000-0000-000000000000",
    "instance_id": "fabric-instance-123"
}, command="get")
```

**CLI Integration:**
The main program integrates modules through CLI subparsers:

```powershell
# These CLI commands map to module loader calls:
python main.py fabric list -s <subscription_id> -g <resource_group>
# → load_and_run("modules.fabric", args, "list")

python main.py fabric get -s <subscription_id> -i <instance_id>  
# → load_and_run("modules.fabric", args, "get")

python main.py powerbi scan-data -s <subscription_id>
# → load_and_run("modules.powerbi", args, "scan-data")
```

## Available Modules

AzureMated includes these built-in cloud service modules:

### **fabric.py** - Microsoft Fabric Operations
- **Manager Class**: `FabricManager`
- **Azure SDK**: `azure-mgmt-fabric`
- **Operations**: 
  - `list_instances(resource_group=None)`: List Fabric instances
  - `get_instance(instance_id)`: Get specific Fabric instance details
- **CLI Commands**: 
  - `python main.py fabric list -s <subscription_id> [-g <resource_group>]`
  - `python main.py fabric get -s <subscription_id> -i <instance_id>`

### **powerbi.py** - Power BI Premium Operations  
- **Manager Class**: `PowerBIManager`
- **Azure SDK**: `azure-mgmt-powerbidedicated`
- **Operations**:
  - `list_premium_instances(resource_group=None)`: List Power BI Premium instances
  - `get_premium_instance(instance_id)`: Get specific instance details
- **CLI Commands**:
  - `python main.py powerbi list -s <subscription_id> [-g <resource_group>]`
  - `python main.py powerbi scan-data -s <subscription_id> [-i <instance_id>]`

### **azure_topology.py** - Azure Resource Topology
- **Manager Class**: `TopologyManager`  
- **Azure SDK**: `azure-mgmt-resource`
- **Operations**:
  - `get_resource_topology(resource_group=None, resource_type=None)`: Map resource topology
  - `get_resource_dependencies(resource_id)`: Get resource dependencies
- **CLI Commands**:
  - `python main.py topology visualize -s <subscription_id> [-t <resource_type>]`

### **reports.py** - HTML Report Generation
- **Manager Class**: `ReportsManager`
- **Operations**:
  - `run(output_dir='./outputs')`: Assemble existing CSV outputs into an HTML report
- **CLI Commands**:
  - `python main.py report -o <output_dir>`

**Note**: All modules currently have placeholder implementations marked with `# TODO:` comments. The structure and interfaces are established, but the actual Azure SDK integrations need to be implemented.

## Creating New Modules

To create a new cloud service module, follow these steps:

### 1. Create Module File
Create a new Python file in the `modules/` directory:
```powershell
# Example: modules/new_service.py
```

### 2. Follow the Standard Structure
Use the template from [Templates](templates.md) and implement:

```python
"""
New Service Module

Module Structure for Module Loader Compatibility:
[Include the standard compatibility documentation]
"""

from azure.identity import ChainedTokenCredential
from azure.core.exceptions import AzureError
import logging

log = logging.getLogger("fabric_friend")

class NewServiceManager:
    """Manager class for the new cloud service."""
    
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        self.credential = credential
        self.subscription_id = subscription_id
        # Initialize Azure SDK client here
        
    def list_resources(self, resource_group=None):
        """List resources for this service."""
        # Implement using appropriate Azure SDK
        pass

# Global singleton
_newservice_manager = None

def run(subscription_id=None, **kwargs):
    """Required entry point function."""
    # Standard implementation pattern
    pass

# Optional command functions
def list(subscription_id=None, resource_group=None, **kwargs):
    """Optional: Specific list command."""
    pass
```

### 3. Update Module Package
Add your new manager to `modules/__init__.py`:
```python
from .new_service import NewServiceManager
```

### 4. Add CLI Integration
Update `main.py` to add CLI commands for your module:
```python
# Add to main() function in main.py
newservice_parser = subparsers.add_parser("newservice", help="New Service operations")
newservice_subparsers = newservice_parser.add_subparsers(dest="command", help="Command to run")

# Add specific commands
newservice_list_parser = newservice_subparsers.add_parser("list", help="List resources")
newservice_list_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
newservice_list_parser.add_argument("-g", "--resource-group", help="Resource group name")
```

### 5. Install Required Dependencies
Add any new Azure SDK packages to `requirements.txt`:
```
azure-mgmt-newservice>=1.0.0
```

### 6. Test Your Module
Create tests in `tests/test_newservice_module.py` following the existing test patterns.

## Best Practices

### Module Design
- **Single Responsibility**: Each module should focus on one Azure service or closely related services
- **Consistent Naming**: Use `ServiceManager` naming pattern for manager classes
- **Error Handling**: Implement comprehensive error handling with Azure-specific exceptions
- **Logging**: Use the standard logger: `log = logging.getLogger("fabric_friend")`

### Interface Compliance
- **Required Function**: Always implement the `run()` function at module level
- **Parameter Validation**: Validate `subscription_id` is provided before proceeding
- **Return Format**: Return consistent dictionary structures with meaningful keys
- **Documentation**: Include comprehensive docstrings following Google/NumPy style

### Azure SDK Integration
- **Credential Injection**: Always accept `ChainedTokenCredential` in manager constructor
- **Client Initialization**: Initialize Azure SDK clients in manager constructor
- **Resource Management**: Use appropriate Azure SDK packages (e.g., `azure-mgmt-*`)
- **Exception Handling**: Catch and handle `AzureError` and service-specific exceptions

### Performance Considerations
- **Singleton Pattern**: Use module-level singleton for manager instances
- **Credential Reuse**: Reuse credentials across module calls
- **Lazy Loading**: Only initialize heavy resources when needed
- **Caching**: Consider caching for expensive operations (with appropriate TTL)

### Testing
- **Unit Tests**: Test module loading and interface compliance
- **Mock Dependencies**: Mock Azure SDK calls to avoid real API calls in tests
- **Integration Tests**: Test the full flow from CLI to module execution
- **Error Testing**: Test error conditions and edge cases

### Security
- **Credential Handling**: Never log or expose credentials
- **Input Validation**: Validate and sanitize all input parameters
- **Least Privilege**: Request minimal required permissions for operations

## See Also

- [Architecture Overview](architecture.md)
- [Utilities](utilities.md)
- [Templates](templates.md)
