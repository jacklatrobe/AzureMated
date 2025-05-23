# FabricFriend

A console application for Microsoft Fabric and Power BI management using the Azure Python SDK.

## Description

FabricFriend is a command-line tool that helps you manage and monitor Microsoft Fabric instances and Power BI Premium resources in your Azure environment. It provides commands for listing resources, checking authentication status, and running specialized modules.

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/FabricFriend.git
cd FabricFriend

# Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

FabricFriend provides several commands:

```powershell
# Check authentication
python main.py auth

# List Microsoft Fabric instances
python main.py fabric -s <subscription_id> [-g <resource_group>]

# List Power BI Premium instances
python main.py powerbi -s <subscription_id> [-g <resource_group>]

# Run a module
python main.py run <module_name> -s <subscription_id> [additional params]
```

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

- [Getting Started](docs/getting-started.md)
- [Architecture Overview](docs/architecture.md)
- [Module System](docs/modules.md)
- [Utilities](docs/utilities.md)
- [Authentication](docs/authentication.md)
- [Templates](docs/templates.md)

## Features

- Authentication with Azure using ChainedTokenCredential
- Microsoft Fabric instance management
- Power BI Premium instance management
- Azure resource topology visualization
- Modular architecture for easy extension
- Dynamic module loading system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
