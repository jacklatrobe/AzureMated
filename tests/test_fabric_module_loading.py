"""
Tests for the fabric module loading (not testing module functionality)
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.module_loader import load_and_run


class TestFabricModuleLoading:
    """Test class for fabric module loading (not testing module functionality)"""

    def test_fabric_module_list_command(self):
        """Test that the fabric module can be loaded and the list command called"""
        # Mock the FabricManager class
        mock_manager = MagicMock()
        mock_manager.list_instances.return_value = [
            {"id": "fabric1", "name": "Fabric Instance 1", "location": "westus"},
            {"id": "fabric2", "name": "Fabric Instance 2", "location": "eastus"}
        ]
        
        # Mock the _fabric_manager global variable
        with patch('modules.fabric._fabric_manager', None):
            # Mock initialize_credential to avoid actual authentication
            with patch('modules.fabric.initialize_credential', return_value=MagicMock()):
                # Mock FabricManager to return our mock manager
                with patch('modules.fabric.FabricManager', return_value=mock_manager):
                    # Call load_and_run with the fabric module
                    result = load_and_run(
                        'modules.fabric',
                        {'subscription_id': 'test-subscription', 'resource_group': 'test-rg'},
                        'list'
                    )
                    
                    # Verify that the manager's list_instances method was called
                    mock_manager.list_instances.assert_called_once_with('test-rg')
                    
                    # Verify the result structure
                    assert 'instances' in result
                    assert len(result['instances']) == 2
                    assert result['instances'][0]['name'] == 'Fabric Instance 1'
                    assert result['instances'][1]['name'] == 'Fabric Instance 2'

    def test_fabric_module_get_command(self):
        """Test that the fabric module can be loaded and the get command called"""
        # Mock the FabricManager class
        mock_manager = MagicMock()
        mock_manager.get_instance.return_value = {
            "id": "fabric1", 
            "name": "Fabric Instance 1", 
            "location": "westus",
            "properties": {
                "provisioningState": "Succeeded",
                "capacity": 10
            }
        }
        
        # Mock the _fabric_manager global variable
        with patch('modules.fabric._fabric_manager', None):
            # Mock initialize_credential to avoid actual authentication
            with patch('modules.fabric.initialize_credential', return_value=MagicMock()):
                # Mock FabricManager to return our mock manager
                with patch('modules.fabric.FabricManager', return_value=mock_manager):
                    # Call load_and_run with the fabric module
                    result = load_and_run(
                        'modules.fabric',
                        {'subscription_id': 'test-subscription', 'instance_id': 'fabric1'},
                        'get'
                    )
                    
                    # Verify that the manager's get_instance method was called
                    mock_manager.get_instance.assert_called_once_with('fabric1')
                    
                    # Verify the result structure
                    assert 'instance' in result
                    assert result['instance']['id'] == 'fabric1'
                    assert result['instance']['name'] == 'Fabric Instance 1'
                    assert result['instance']['properties']['capacity'] == 10

    def test_fabric_module_run_default(self):
        """Test that the fabric module's default run method works"""
        # Mock the FabricManager class
        mock_manager = MagicMock()
        mock_manager.list_instances.return_value = []
        mock_manager.get_instance.return_value = {"id": "fabric1", "name": "Fabric Instance 1"}
        
        # Mock the _fabric_manager global variable
        with patch('modules.fabric._fabric_manager', None):
            # Mock initialize_credential to avoid actual authentication
            with patch('modules.fabric.initialize_credential', return_value=MagicMock()):
                # Mock FabricManager to return our mock manager
                with patch('modules.fabric.FabricManager', return_value=mock_manager):
                    # Call load_and_run with the fabric module - with instance_id
                    result1 = load_and_run(
                        'modules.fabric',
                        {'subscription_id': 'test-subscription', 'instance_id': 'fabric1'}
                    )
                    
                    # Verify get_instance was called
                    mock_manager.get_instance.assert_called_once_with('fabric1')
                    assert 'instance' in result1
                    
                    # Reset the mock
                    mock_manager.reset_mock()
                    
                    # Call load_and_run with the fabric module - without instance_id
                    result2 = load_and_run(
                        'modules.fabric',
                        {'subscription_id': 'test-subscription', 'resource_group': 'test-rg'}
                    )
                    
                    # Verify list_instances was called
                    mock_manager.list_instances.assert_called_once_with('test-rg')
                    assert 'instances' in result2
