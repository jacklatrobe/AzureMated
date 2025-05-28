# Authentication

AzureMated uses Azure identity libraries to authenticate with Azure services.

## Authentication Flow

The application uses a chain of credential providers to authenticate with Azure:

```
┌─────────────────┐
│ User Input      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ ChainedToken    │
│ Credential      │
└─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Azure CLI       │────▶│ Azure Developer │
│ Credential      │     │ CLI Credential  │
└─────────────────┘     └─────────────────┘
```

## Authentication Methods

### Azure CLI Credential

Uses the Azure CLI (`az`) authentication context. This is tried first and requires:

1. Azure CLI to be installed
2. User to be logged in (`az login`)

### Azure Developer CLI Credential

Uses the Azure Developer CLI (`azd`) authentication context. This is tried if Azure CLI credential fails and requires:

1. Azure Developer CLI to be installed
2. User to be logged in (`azd auth login`)

## Implementation

Authentication is implemented in `utils/auth.py`:

```python
def initialize_credential():
    """
    Initialize the Azure credential using a chain of authentication methods.
    Falls back to subsequent methods if earlier ones fail.
    
    Returns:
        ChainedTokenCredential: The credential object for Azure authentication
    """
    try:
        # Using chained credentials
        credential = ChainedTokenCredential(
            AzureCliCredential(),
            AzureDeveloperCliCredential()
        )
        
        # Test the credential
        ResourceManagementClient(credential, subscription_id="00000000-0000-0000-0000-000000000000")
        
        return credential
        
    except Exception as e:
        log.error(f"Authentication failed: {str(e)}")
        sys.exit(1)
```

## Usage

Authentication is handled automatically by the application:

1. The `initialize_credential()` function is called when needed
2. It returns a `ChainedTokenCredential` that can be used with Azure SDK clients
3. If authentication fails, the application exits with an error message

You can also explicitly check authentication status with the `auth` command:

```powershell
python main.py auth
```

## Future Enhancements

Planned authentication enhancements include:

- Support for Microsoft 365 authentication
- Interactive browser authentication
- Service principal authentication
- Managed identity support (for cloud deployments)

## See Also

- [Getting Started](getting-started.md)
- [Utilities](utilities.md)
