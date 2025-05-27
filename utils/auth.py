"""
Authentication Utilities

This module contains functions for authenticating with Azure using CLI credentials and MSAL.
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

def get_msal_token(scopes):
    """
    Acquire and cache an access token for the specified scopes using MSAL with device flow.
    Requires FABRICFRIEND_CLIENT_ID and FABRICFRIEND_TENANT_ID environment variables.
    Returns:
        str: Access token
    """
    import os
    from msal import PublicClientApplication, SerializableTokenCache

    # Configuration from environment
    client_id = os.getenv("FABRICFRIEND_CLIENT_ID")
    tenant_id = os.getenv("FABRICFRIEND_TENANT_ID")
    if not client_id or not tenant_id:
        raise Exception("Environment variables FABRICFRIEND_CLIENT_ID and FABRICFRIEND_TENANT_ID must be set for MSAL authentication")
    # Token cache file
    cache_path = os.path.expanduser("~/.fabricfriend_token_cache.bin")
    cache = SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r").read())
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = PublicClientApplication(client_id, authority=authority, token_cache=cache)

    # Attempt silent auth
    result = app.acquire_token_silent(scopes, account=None)
    if not result:
        # Interactive device code flow
        flow = app.initiate_device_flow(scopes=scopes)
        if "message" in flow:
            print(flow["message"], flush=True)
        result = app.acquire_token_by_device_flow(flow)

    if not result or "access_token" not in result:
        error = result.get("error_description") if result else "Unknown error"
        raise Exception(f"Failed to acquire MSAL token: {error}")

    # Persist cache
    with open(cache_path, "w") as f:
        f.write(cache.serialize())

    return result["access_token"]
