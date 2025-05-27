# Utilities

FabricFriend includes a set of utility functions and classes that provide common functionality across the application.

## Overview

The utilities are organized in the `utils` directory and provide functionality for:

- Authentication
- Display and formatting
- Module loading
- Common operations
- CSV writing

## Authentication Utilities (`auth.py`)

### `initialize_credential()`

Creates a `ChainedTokenCredential` for authenticating with Azure services:

```python
from utils import initialize_credential

# Get credential
credential = initialize_credential()
```

This function sets up a chain of credential providers:
1. Azure CLI Credential
2. Azure Developer CLI Credential

### `check_azure_auth()`

Verifies if Azure authentication is working:

```python
from utils import check_azure_auth

# Check authentication
is_authenticated = check_azure_auth()
```

### `check_microsoft365_auth()`

Placeholder for checking Microsoft 365 authentication (not yet implemented).

## Display Utilities (`common.py`)

### `console`

A Rich console instance for styled output:

```python
from utils import console

# Print styled text
console.print("[bold]Hello World[/bold]")
```

### `format_table(data, title, columns)`

Formats data as a Rich table:

```python
from utils import format_table

# Format data as a table
data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
columns = {"id": "ID", "name": "Name"}
table = format_table(data, "Items", columns)
```

### `display_results(data, title, columns)`

Displays data as a Rich table:

```python
from utils import display_results

# Display results
display_results(data, "Items", {"id": "ID", "name": "Name"})
```

## Module Loader (`module_loader.py`)

### `load_and_run(module_name, args)`

Dynamically loads a module and executes its run function:

```python
from utils import load_and_run

# Load and run a module
result = load_and_run("modules.fabric", {
    "subscription_id": "00000000-0000-0000-0000-000000000000",
    "resource_group": "my-resource-group"
})
```

## CSV Writer Utilities (`csv_writer.py`)

### `write_csv_with_schema(file_path, data, schema)`

Writes data to a CSV file with a predefined schema. This allows modules to define their own CSV schemas and ensure consistent file structure:

```python
from utils.csv_writer import write_csv_with_schema

# Define schema for the data
schema = ['id', 'name', 'location', 'type']

# Write data with schema
write_csv_with_schema("output.csv", data_list, schema)
```

### `write_csv(file_path, data)`

Backward-compatible CSV writer that derives headers from data keys:

```python
from utils.csv_writer import write_csv

# Write data without predefined schema
write_csv("output.csv", data_list)
```

### Benefits of Schema-Based CSV Writing

- **Consistency**: Each module defines its own schema, ensuring consistent column order
- **Empty File Handling**: Creates files with proper headers even when no data is available
- **Modularity**: No circular dependencies - modules pass their schema to the utility
- **Flexibility**: Accommodates additional columns in data that aren't in the base schema

## Usage in Main Program

The utilities are used throughout the main program to:

- Authenticate with Azure
- Parse command-line arguments
- Display results
- Load and execute modules
- Write CSV files with module-specific schemas

## See Also

- [Architecture Overview](architecture.md)
- [Module System](modules.md)
- [Authentication](authentication.md)
