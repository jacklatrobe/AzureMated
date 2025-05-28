# AzureMated: Project Summary for Architects

This document provides a comprehensive overview of the AzureMated project structure and patterns for architects building new cloud service modules.

## Project Overview

**AzureMated** is a modular console application for managing Azure cloud services, specifically designed for Microsoft Fabric, Power BI, and other Azure resources. The architecture emphasizes:

- **Modularity**: Each cloud service is a separate, self-contained module
- **Consistency**: All modules follow identical interface patterns
- **Extensibility**: New services can be added without modifying core code
- **CLI Integration**: Docker-like command structure for intuitive usage

## Architecture Summary

```
User CLI Command
       ↓
   main.py (CLI Parser)
       ↓
   run_module() function
       ↓
   utils/module_loader.py (Dynamic Loading)
       ↓
   modules/[service].py (Cloud Service Module)
       ↓
   Azure SDK Client
       ↓
   Azure Service API
```

## Module Development Pattern

Every cloud service module follows this exact pattern:

### 1. File Structure
```
modules/
├── __init__.py                 # Package imports
├── fabric.py                   # Microsoft Fabric module
├── powerbi.py                  # Power BI Premium module  
├── azure_topology.py           # Resource topology module
└── your_new_service.py         # Your new service module
```

### 2. Module Components (Required)

#### A. Manager Class
```python
class YourServiceManager:
    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        self.credential = credential
        self.subscription_id = subscription_id
        # Initialize Azure SDK client
```

#### B. Global Singleton
```python
_yourservice_manager = None  # Module-level singleton
```

#### C. Required `run` Function
```python
def run(subscription_id=None, **kwargs):
    """Entry point called by module loader"""
    # Standard implementation pattern
    return {"result": "success", "data": [...]}
```

#### D. Optional Command Functions
```python
def list(subscription_id=None, resource_group=None, **kwargs):
    """Called for: python main.py yourservice list"""
    
def get(subscription_id=None, resource_id=None, **kwargs):
    """Called for: python main.py yourservice get"""
```

### 3. Integration Points

#### A. Module Package (`modules/__init__.py`)
```python
from .your_new_service import YourServiceManager
```

#### B. CLI Integration (`main.py`)
```python
# Add subparser for your service
yourservice_parser = subparsers.add_parser("yourservice", help="Your Service operations")
yourservice_subparsers = yourservice_parser.add_subparsers(dest="command")

# Add commands
list_parser = yourservice_subparsers.add_parser("list", help="List resources")
list_parser.add_argument("-s", "--subscription-id", required=True)
```

#### C. Dependencies (`requirements.txt`)
```
azure-mgmt-yourservice>=1.0.0
```

## Development Workflow

### Phase 1: Planning
1. Identify Azure SDK package for your service
2. Define key operations (list, get, create, etc.)
3. Plan CLI command structure

### Phase 2: Implementation
1. Copy template from `docs/templates.md`
2. Implement Manager class with Azure SDK
3. Implement required `run()` function
4. Add optional command functions

### Phase 3: Integration
1. Update `modules/__init__.py`
2. Add CLI commands to `main.py`
3. Update `requirements.txt`

### Phase 4: Testing
1. Create unit tests in `tests/` directory
2. Test module loading: `from utils import load_and_run`
3. Test CLI commands: `python main.py yourservice list`

## Key Implementation Patterns

### 1. Authentication Pattern
```python
from utils import initialize_credential

credential = initialize_credential()  # Handles Azure CLI/azd auth
manager = YourServiceManager(credential, subscription_id)
```

### 2. Error Handling Pattern
```python
from azure.core.exceptions import AzureError

try:
    result = self.client.operation()
except AzureError as e:
    log.error(f"Azure error: {str(e)}")
    raise
```

### 3. Logging Pattern
```python
import logging
log = logging.getLogger("fabric_friend")

log.info("Performing operation")
log.error("Error occurred")
```

### 4. Return Format Pattern
```python
# For list operations
return {"resources": [...]}
return {"instances": [...]}

# For get operations  
return {"resource": {...}}
return {"instance": {...}}

# For custom operations
return {"result": "success", "data": {...}}
```

## Testing Strategy

### Unit Tests
- Module loading and interface compliance
- Manager class initialization
- Function parameter validation
- Return format consistency

### Integration Tests
- CLI command parsing
- Module loader execution
- End-to-end command flow

### Mock Strategy
- Mock Azure SDK clients to avoid real API calls
- Test error conditions and edge cases
- Validate parameter passing and return formats

## Current Implementation Status

### Completed Modules
- **fabric.py**: Structure complete, Azure SDK integration pending
- **powerbi.py**: Structure complete, Azure SDK integration pending  
- **azure_topology.py**: Structure complete, resource mapping pending

### Module Characteristics
- All modules follow identical patterns
- Placeholder implementations marked with `# TODO:`
- Ready for Azure SDK integration
- CLI integration complete
- Unit test framework established

## Resources for New Module Development

### Essential Documentation
1. **[Module Development Guide](module-development-guide.md)**: Complete step-by-step process
2. **[Templates](templates.md)**: Boilerplate code with comprehensive examples
3. **[Module System](modules.md)**: Interface requirements and patterns
4. **[Architecture](architecture.md)**: System design and data flow

### Code References
- **Existing Modules**: `modules/fabric.py`, `modules/powerbi.py` for patterns
- **Module Loader**: `utils/module_loader.py` for loading mechanism
- **CLI Integration**: `main.py` for command structure
- **Tests**: `tests/test_*_module*.py` for testing patterns

### Development Tools
- **Template**: Use `docs/templates.md` as starting point
- **Testing**: Run `python run_tests.py` for validation
- **CLI Testing**: Use `python main.py yourservice command` format

## Key Success Factors

1. **Follow Exact Patterns**: Use existing modules as reference
2. **Interface Compliance**: Implement required functions exactly as specified
3. **Error Handling**: Use Azure-specific exception handling
4. **Documentation**: Update all relevant documentation files
5. **Testing**: Create comprehensive unit tests
6. **CLI Integration**: Ensure commands work end-to-end

## Support and Validation

- **Module Validation**: Use `load_and_run()` to test module loading
- **CLI Validation**: Test all command combinations
- **Pattern Validation**: Compare against existing modules for consistency
- **Documentation Validation**: Ensure all docs are updated

This project is designed to make adding new Azure services straightforward by following established patterns. The existing modules provide complete examples of the expected structure and implementation approach.
