"""
Authentication Utilities

This module contains functions for authenticating with Azure and Microsoft 365.
"""

import logging
from azure.identity import (
    ChainedTokenCredential,
    AzureCliCredential,
    AzureDeveloperCliCredential,
)
from azure.core.exceptions import AzureError

log = logging.getLogger("fabric_friend")

def initialize_credential():
    """
    Initialize the Azure credential using a chain of authentication methods.
    Falls back to subsequent methods if earlier ones fail.
    
    Returns:
        ChainedTokenCredential: The credential object for Azure authentication
    """
    # Create chained credentials
    credential = ChainedTokenCredential(
        AzureCliCredential(),
        AzureDeveloperCliCredential()
    )
    try:
        # Test credential by requesting a token for Azure management
        credential.get_token("https://management.azure.com/.default")
        log.info("✅ Successfully authenticated with Azure")
        return credential
    except Exception as e:
        log.error(f"❌ Authentication failed: {str(e)}")
        log.info("Please login using 'az login' or 'azd auth login' and try again.")
        # Propagate exception for check_azure_auth to handle
        raise

def check_azure_auth():
    """
    Check authentication status with Azure.
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    try:
        initialize_credential()
        return True
    except Exception:
        return False

def check_microsoft365_auth():
    """
    Check authentication status with Microsoft 365.
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    # TODO: Implement Microsoft 365 authentication check
    return False
