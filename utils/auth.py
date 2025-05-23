"""
Authentication Utilities

This module contains functions for authenticating with Azure and Microsoft 365.
"""

import sys
import logging
from azure.identity import (
    ChainedTokenCredential,
    AzureCliCredential,
    AzureDeveloperCliCredential,
)
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError

log = logging.getLogger("fabric_friend")

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
        
        # Test the credential to make sure it works
        # This will throw an exception if authentication fails
        ResourceManagementClient(credential, subscription_id="00000000-0000-0000-0000-000000000000")._client.config.retry_policy.retries = 0
        ResourceManagementClient(credential, subscription_id="00000000-0000-0000-0000-000000000000").resource_groups.list().__next__
        
        log.info("✅ Successfully authenticated with Azure")
        return credential
        
    except Exception as e:
        log.error(f"❌ Authentication failed: {str(e)}")
        log.info("Please login using 'az login' or 'azd auth login' and try again.")
        sys.exit(1)

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
