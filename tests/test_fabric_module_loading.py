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
        
        # Add a list command to the module that calls the manager
        with patch('modules.fabric._fabric_manager', None):
            with patch('utils.initialize_credential', return_value=MagicMock()):
                with patch('modules.fabric.FabricManager', return_value=mock_manager):
                    # Dynamically add the list method to the module
                    with patch('modules.fabric.list', create=True) as mock_list:
                        mock_list.return_value = {"instances": mock_manager.list_instances.return_value}
                        
                        # Call load_and_run with the fabric module and list command
                        result = load_and_run(
                            'modules.fabric',
                            {'subscription_id': 'test-subscription', 'resource_group': 'test-rg'},
                            'list'
                        )
                        
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
        
        # Add a get command to the module that calls the manager
        with patch('modules.fabric._fabric_manager', None):
            with patch('utils.initialize_credential', return_value=MagicMock()):
                with patch('modules.fabric.FabricManager', return_value=mock_manager):
                    # Dynamically add the get method to the module
                    with patch('modules.fabric.get', create=True) as mock_get:
                        mock_get.return_value = {"instance": mock_manager.get_instance.return_value}
                        
                        # Call load_and_run with the fabric module and get command
                        result = load_and_run(
                            'modules.fabric',
                            {'subscription_id': 'test-subscription', 'instance_id': 'fabric1'},
                            'get'
                        )
                        
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
        
        # Test the run method of the module
        with patch('modules.fabric._fabric_manager', None):
            with patch('utils.initialize_credential', return_value=MagicMock()):
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
