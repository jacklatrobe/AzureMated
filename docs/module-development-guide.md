# Module Development Guide

This guide provides comprehensive instructions for developing new cloud service modules for FabricFriend.

## Overview

FabricFriend uses a modular architecture where each Azure service is implemented as a separate module. This guide walks through creating a new module from start to finish, using Microsoft Fabric as an example.

## Prerequisites

- Understanding of Python and Azure SDK patterns
- Familiarity with the Azure service you're implementing
- Access to Azure subscription for testing
- Development environment set up per [Getting Started](getting-started.md)

## Development Process

### Phase 1: Planning and Setup

1. **Identify the Azure Service**
   - Determine the Azure SDK package name (e.g., `azure-mgmt-fabric`)
   - Identify key operations (list, get, create, delete, custom operations)
   - Review Azure SDK documentation and examples

2. **Define Module Interface**
   - Plan the Manager class name and methods
   - Determine CLI command structure
   - Define input parameters and return formats

3. **Set Up Development Environment**
   ```powershell
   # Install Azure SDK package
   pip install azure-mgmt-fabric>=1.0.0
   
   # Update requirements.txt
   Add-Content requirements.txt "azure-mgmt-fabric>=1.0.0"
   ```

### Phase 2: Implementation

1. **Create Module File**
   ```powershell
   # Start with template
   Copy-Item docs\templates.md modules\fabric.py
   ```

2. **Implement Manager Class**
   ```python
   from azure.mgmt.fabric import FabricManagementClient
   
   class FabricManager:
       def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
           self.credential = credential
           self.subscription_id = subscription_id
           self.client = FabricManagementClient(credential, subscription_id)
       
       def list_instances(self, resource_group=None):
           """Implementation using Azure SDK"""
           try:
               if resource_group:
                   instances = self.client.instances.list_by_resource_group(resource_group)
               else:
                   instances = self.client.instances.list()
               return [instance.as_dict() for instance in instances]
           except AzureError as e:
               log.error(f"Error listing Fabric instances: {str(e)}")
               raise
   ```

3. **Implement Required Functions**
   ```python
   def run(subscription_id=None, resource_group=None, instance_id=None, **kwargs):
       """Standard entry point implementation"""
       # Follow the pattern from existing modules
       
   def list(subscription_id=None, resource_group=None, **kwargs):
       """Optional: Specific list command"""
       
   def get(subscription_id=None, instance_id=None, **kwargs):
       """Optional: Specific get command"""
   ```

### Phase 3: CLI Integration

1. **Update main.py**
   ```python
   # Add to main() function
   fabric_parser = subparsers.add_parser("fabric", help="Microsoft Fabric operations")
   fabric_subparsers = fabric_parser.add_subparsers(dest="command", help="Command to run")
   
   # Add commands
   fabric_list_parser = fabric_subparsers.add_parser("list", help="List Fabric instances")
   fabric_list_parser.add_argument("-s", "--subscription-id", required=True)
   fabric_list_parser.add_argument("-g", "--resource-group", help="Resource group name")
   ```

2. **Update modules/__init__.py**
   ```python
   from .fabric import FabricManager
   ```

### Phase 4: Testing

1. **Create Unit Tests**
   ```python
   # tests/test_fabric_module.py
   class TestFabricModule:
       def test_fabric_manager_initialization(self):
           """Test manager creation"""
           
       def test_list_instances(self):
           """Test listing functionality"""
           
       def test_module_loading(self):
           """Test module loader integration"""
   ```

2. **Test Module Loading**
   ```powershell
   # Test through module loader
   python -c "from utils import load_and_run; print(load_and_run('modules.fabric', {'subscription_id': 'test'}))"
   ```

3. **Test CLI Integration**
   ```powershell
   # Test CLI commands
   python main.py fabric list -s test-subscription-id
   python main.py fabric get -s test-subscription-id -i test-instance-id
   ```

### Phase 5: Documentation and Finalization

1. **Update Documentation**
   - Add module to [Available Modules](modules.md#available-modules) section
   - Document any service-specific parameters or behaviors
   - Add examples to [Getting Started](getting-started.md)

2. **Code Review Checklist**
   - [ ] Follows module structure requirements
   - [ ] Implements required `run()` function
   - [ ] Uses singleton pattern for manager instance
   - [ ] Handles errors appropriately
   - [ ] Includes comprehensive logging
   - [ ] Has unit tests
   - [ ] CLI integration works
   - [ ] Documentation updated

## Advanced Topics

### Custom Operations

For service-specific operations, implement additional command functions:

```python
def scan_data(subscription_id=None, instance_id=None, **kwargs):
    """Custom operation for Fabric data scanning"""
    global _fabric_manager
    
    if not subscription_id:
        raise ValueError("Subscription ID is required")
    
    credential = initialize_credential()
    if _fabric_manager is None or _fabric_manager.subscription_id != subscription_id:
        _fabric_manager = FabricManager(credential, subscription_id)
    
    # Implement custom operation
    return {"scanned_data": _fabric_manager.scan_instance_data(instance_id)}
```

### Error Handling Patterns

```python
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

def get_instance(self, instance_id):
    try:
        instance = self.client.instances.get(instance_id)
        return instance.as_dict()
    except ResourceNotFoundError:
        log.warning(f"Fabric instance not found: {instance_id}")
        return None
    except ClientAuthenticationError:
        log.error("Authentication failed for Fabric API")
        raise
    except AzureError as e:
        log.error(f"Azure error getting Fabric instance {instance_id}: {str(e)}")
        raise
```

### Performance Optimization

```python
class FabricManager:
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        self.credential = credential
        self.subscription_id = subscription_id
        self._client = None  # Lazy initialization
        self._cache = {}     # Simple caching
    
    @property
    def client(self):
        if self._client is None:
            self._client = FabricManagementClient(self.credential, self.subscription_id)
        return self._client
    
    def list_instances(self, resource_group=None, use_cache=True):
        cache_key = f"instances_{resource_group}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Fetch from API
        instances = self._fetch_instances(resource_group)
        self._cache[cache_key] = instances
        return instances
```

### CSV Output Patterns

When your module needs to write CSV output files, use the centralized CSV writer utility:

```python
from utils.csv_writer import write_csv_with_schema

# Define schema for your module's CSV files
MODULE_CSV_SCHEMAS = {
    'instances': ['id', 'name', 'location', 'resource_group', 'status', 'created_date'],
    'configurations': ['instance_id', 'setting_name', 'setting_value', 'last_modified'],
    'default': ['id', 'name', 'type']
}

def collect_data(subscription_id=None, output_dir="./outputs", **kwargs):
    """Example function that writes CSV output"""
    # Collect your data
    instances = _manager.list_instances()
    configurations = _manager.get_configurations()
    
    # Write CSV files with schema
    os.makedirs(output_dir, exist_ok=True)
    write_csv_with_schema(
        os.path.join(output_dir, "instances.csv"), 
        instances, 
        MODULE_CSV_SCHEMAS['instances']
    )
    write_csv_with_schema(
        os.path.join(output_dir, "configurations.csv"), 
        configurations, 
        MODULE_CSV_SCHEMAS['configurations']
    )
```

#### Benefits of Schema-Based CSV Writing
- **Consistency**: Ensures consistent column order across runs
- **Empty File Handling**: Creates files with headers even when no data is available
- **No Circular Dependencies**: Modules define their own schemas and pass them to the utility
- **Visualization Support**: Other utilities can accept schemas as parameters

## Troubleshooting

### Common Issues

1. **Module Not Loading**
   - Check module is in `modules/` directory
   - Verify `run()` function exists at module level
   - Check for syntax errors in module file

2. **Authentication Errors**
   - Verify Azure CLI is logged in: `az account show`
   - Check subscription ID is valid
   - Ensure proper permissions for the service

3. **Import Errors**
   - Install required Azure SDK package
   - Add package to `requirements.txt`
   - Check package version compatibility

4. **CLI Commands Not Working**
   - Verify subparser is added in `main.py`
   - Check argument names match function parameters
   - Ensure `dest="command"` is set for subparsers

### Debugging Tips

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test module directly
from modules.fabric import run
result = run(subscription_id="test")

# Test with module loader
from utils import load_and_run
result = load_and_run("modules.fabric", {"subscription_id": "test"})
```

## See Also

- [Module System](modules.md)
- [Templates](templates.md)
- [Architecture Overview](architecture.md)
- [Testing Guide](../tests/README.md)
