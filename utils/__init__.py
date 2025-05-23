"""
FabricFriend utilities package
"""

from .auth import initialize_credential, check_azure_auth, check_microsoft365_auth
from .common import console, format_table, display_results
from .module_loader import load_and_run
