"""
Power BI Module

This module implements a small wrapper around the Power BI Admin REST APIs. It
collects organization wide metadata such as capacities, workspaces, users,
dashboards, dataflows and datasets. The results are written to CSV files and a
summary is printed to the console when the module's ``run`` function is
executed.

Module Structure for Module Loader Compatibility:
-------------------------------------------------
1. Each module must define a 'run' function at the module level that serves as the entry point
2. The 'run' function must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
3. The 'run' function should return a dictionary with results
4. The module typically defines a manager class to encapsulate module-specific functionality
5. The module should maintain a singleton instance of the manager for efficiency

When creating new modules, follow this pattern to ensure compatibility with the module_loader.
"""

from azure.identity import ChainedTokenCredential
from azure.core.exceptions import AzureError
from utils.auth import get_msal_token, get_credential_token
from utils.csv_writer import write_csv_with_schema
import logging
import os
from typing import List, Dict, Optional
import requests

log = logging.getLogger("fabric_friend")

# Define schemas for different Power BI CSV file types
POWERBI_CSV_SCHEMAS = {
    'capacities': ['id', 'display_name', 'admins', 'sku', 'state', 'region'],
    'workspaces': ['id', 'name', 'type', 'state', 'is_read_only', 'is_on_dedicated_capacity', 'capacity_id'],
    'workspace_users': ['workspace_id', 'workspace_name', 'group_user_access_right', 'email_address', 'display_name', 'identifier', 'principal_type', 'user_type'],
    'dashboards': ['id', 'display_name', 'workspace_id', 'workspace_name', 'embed_url', 'is_read_only', 'web_url'],
    'dataflows': ['object_id', 'name', 'description', 'workspace_id', 'workspace_name', 'configured_by', 'modified_by', 'modified_date_time'],
    'datasets': ['id', 'name', 'workspace_id', 'workspace_name', 'add_rows_api_enabled', 'configured_by', 'created_date', 'is_refreshable', 'is_effective_identity_required', 'is_effective_identity_roles_required', 'is_on_prem_gateway_required'],
    # Generic fallback for unknown file types
    'default': ['id', 'name', 'type']
}

class PowerBIManager:
    """Manager for interacting with the Power BI Admin REST API."""

    ADMIN_BASE_URL = "https://api.powerbi.com/v1.0/myorg/admin"

    def __init__(self, credential: ChainedTokenCredential, subscription_id: str):
        self.credential = credential
        self.subscription_id = subscription_id
        self._token: Optional[str] = None    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _get_access_token(self) -> str:
        """Acquire an access token for the Power BI API."""
        if self._token:
            return self._token
            
        scope = "https://analysis.windows.net/powerbi/api/.default"
        
        # First try to get token directly from the credential (service principal)
        try:
            log.info("Attempting to get token directly from credential (service principal)")
            token = get_credential_token(self.credential, [scope])
            self._token = token
            return token
        except Exception as e:
            log.info(f"Failed to get token from credential, falling back to MSAL: {str(e)}")
            
        # Fall back to MSAL authentication
        try:
            log.info("Attempting to get token via MSAL")
            token = get_msal_token([scope])
            self._token = token
            return token
        except Exception as e:
            raise Exception(f"Failed to acquire token for Power BI API: {str(e)}")
    
    def _api_get(self, path: str, params: Optional[Dict[str, str]] = None) -> List[Dict]:
        """Call a Power BI Admin GET endpoint and return the aggregated results."""
        url = f"{self.ADMIN_BASE_URL}/{path.lstrip('/')}"
        
        try:
            headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        except Exception as e:
            log.error(f"Failed to get access token: {str(e)}")
            raise AzureError(
                "Failed to authenticate with Power BI API. This API requires a service principal with the 'Power BI Service Administrator' role."
            )

        results: List[Dict] = []
        try:
            while url:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    error_message = f"Power BI API request failed: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_message += f" - {error_detail.get('error', {}).get('message', response.text)}"
                    except:
                        error_message += f" - {response.text}"
                    raise AzureError(error_message)

                data = response.json()
                items = data.get("value", [])
                results.extend(items)

                url = data.get("@odata.nextLink") or data.get("nextLink")
                params = None  # Only needed on first request
        except Exception as e:
            if "Permission" in str(e) or "401" in str(e) or "403" in str(e):
                log.error("Access denied. Make sure your account or service principal has Power BI Admin permissions.")
            raise

        return results

    # ------------------------------------------------------------------
    # Admin API operations
    # ------------------------------------------------------------------
    def get_capacities(self) -> List[Dict]:
        """Return a list of capacities for the organization."""
        log.info("Fetching capacities")
        return self._api_get("capacities")

    def get_groups(self) -> List[Dict]:
        """Return a list of workspaces for the organization."""
        log.info("Fetching workspaces")
        return self._api_get("groups")

    def get_group_users(self, group_id: str) -> List[Dict]:
        """Return a list of users that have access to the specified workspace."""
        log.debug(f"Fetching users for workspace {group_id}")
        return self._api_get(f"groups/{group_id}/users")

    def get_dashboards(self, group_id: str) -> List[Dict]:
        """Return a list of dashboards from the specified workspace."""
        log.debug(f"Fetching dashboards for workspace {group_id}")
        return self._api_get(f"groups/{group_id}/dashboards")

    def get_dataflows(self, group_id: str) -> List[Dict]:
        """Return a list of dataflows from the specified workspace."""
        log.debug(f"Fetching dataflows for workspace {group_id}")
        return self._api_get(f"groups/{group_id}/dataflows")

    def get_datasets(self, group_id: str) -> List[Dict]:
        """Return a list of datasets from the specified workspace."""
        log.debug(f"Fetching datasets for workspace {group_id}")
        return self._api_get(f"groups/{group_id}/datasets")

# Create a Power BI manager instance
_powerbi_manager = None

def _get_schema_for_powerbi_file(file_path: str) -> Optional[List[str]]:
    """Get the appropriate schema for a Power BI CSV file based on its filename."""
    file_name = os.path.basename(file_path)
    
    # Find the matching schema based on filename
    for key in POWERBI_CSV_SCHEMAS:
        if key in file_name:
            return POWERBI_CSV_SCHEMAS[key]
    
    return POWERBI_CSV_SCHEMAS['default']

def run(subscription_id=None, output_dir: str = ".", **kwargs):
    """
    Run the Power BI module functionality.
    
    This function is called by the module_loader and serves as the entry point
    for this module. The module_loader expects this function to exist in all modules
    and will call it with parameters parsed from command line arguments or API calls.
    
    Module Loader Integration:
    - This function must be defined at the module level (not inside a class)
    - It must accept subscription_id as a parameter
    - It should accept **kwargs to handle any additional parameters
    - It must return a dictionary with the results
    
    Args:
        subscription_id: The Azure subscription ID
        output_dir: Directory where CSV files will be written
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with the results of the operation
    """
    from utils import initialize_credential, console
    
    global _powerbi_manager
    
    log.info("Running Power BI Admin data collection")

    # Initialize the credential
    credential = initialize_credential()
    
    # We'll skip acquiring the token here and let the PowerBIManager handle it
    # This allows us to try the credential directly first, then fall back to MSAL if needed    # Create or reuse the Power BI manager
    # Ensure we have a valid subscription_id
    if subscription_id is None:
        subscription_id = "default"  # Use a default value if no subscription_id is provided
    
    if _powerbi_manager is None or _powerbi_manager.subscription_id != subscription_id:
        _powerbi_manager = PowerBIManager(credential, subscription_id)

    try:
        # Fetch organization-wide information
        capacities = _powerbi_manager.get_capacities()
        groups = _powerbi_manager.get_groups()

        users: List[Dict] = []
        dashboards: List[Dict] = []
        dataflows: List[Dict] = []
        datasets: List[Dict] = []

        for g in groups:
            # assume 'id' always present
            gid: str = g["id"]
            users.extend([{"workspaceId": gid, **u} for u in _powerbi_manager.get_group_users(gid)])
            dashboards.extend([{"workspaceId": gid, **d} for d in _powerbi_manager.get_dashboards(gid)])
            dataflows.extend([{"workspaceId": gid, **df} for df in _powerbi_manager.get_dataflows(gid)])
            datasets.extend([{"workspaceId": gid, **ds} for ds in _powerbi_manager.get_datasets(gid)])
    except Exception as e:
        log.error(f"Error fetching Power BI data: {str(e)}")
        log.info("If using a service principal, ensure it has the 'Power BI Service Administrator' role.")
        log.info("If using your user account, ensure FABRICFRIEND_CLIENT_ID and FABRICFRIEND_TENANT_ID environment variables are set.")
        raise Exception(f"Error fetching Power BI data: {str(e)}")

    os.makedirs(output_dir, exist_ok=True)
    write_csv_with_schema(os.path.join(output_dir, "capacities.csv"), capacities, POWERBI_CSV_SCHEMAS['capacities'])
    write_csv_with_schema(os.path.join(output_dir, "workspaces.csv"), groups, POWERBI_CSV_SCHEMAS['workspaces'])
    write_csv_with_schema(os.path.join(output_dir, "workspace_users.csv"), users, POWERBI_CSV_SCHEMAS['workspace_users'])
    write_csv_with_schema(os.path.join(output_dir, "dashboards.csv"), dashboards, POWERBI_CSV_SCHEMAS['dashboards'])
    write_csv_with_schema(os.path.join(output_dir, "dataflows.csv"), dataflows, POWERBI_CSV_SCHEMAS['dataflows'])
    write_csv_with_schema(os.path.join(output_dir, "datasets.csv"), datasets, POWERBI_CSV_SCHEMAS['datasets'])

    summary = {
        "capacities": len(capacities),
        "workspaces": len(groups),
        "workspace_users": len(users),
        "dashboards": len(dashboards),
        "dataflows": len(dataflows),
        "datasets": len(datasets),
    }

    console.print(
        f"[green]Processed {summary['workspaces']} workspaces, {summary['datasets']} datasets, "
        f"{summary['dataflows']} dataflows, {summary['dashboards']} dashboards[/green]"
    )

    return {"summary": summary}
