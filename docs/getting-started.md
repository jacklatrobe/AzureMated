# Getting Started with AzureMated

AzureMated is a console application for Microsoft Fabric and Power BI management using the Azure Python SDK.

## Prerequisites

- Python 3.8+
- Azure CLI or Azure Developer CLI installed and authenticated
- Access to an Azure subscription

## Installation

1. Clone the repository
2. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Basic Usage

AzureMated provides several commands through its command-line interface:

### Authentication Check

```powershell
python main.py auth
```

### List Microsoft Fabric Instances

```powershell
python main.py fabric -s <subscription_id> [-g <resource_group>]
```

### List Power BI Premium Instances

```powershell
python main.py powerbi -s <subscription_id> [-g <resource_group>]
```

### Run a Module

```powershell
python main.py run <module_name> -s <subscription_id> [additional params]
```

Example:
```powershell
python main.py run fabric -s "00000000-0000-0000-0000-000000000000" -g "my-resource-group"
```

## Next Steps

- Learn about the [architecture](architecture.md)
- Understand the [module system](modules.md)
- Explore available [utilities](utilities.md)
