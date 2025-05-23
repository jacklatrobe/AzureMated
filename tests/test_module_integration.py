"""
Tests for module integration to verify that modules can be loaded and executed
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.module_loader import load_and_run


class TestModuleIntegration:
    """Test class for module integration"""

    def test_fabric_module_load(self):
        """Test that the fabric module can be loaded"""
        # Mock the FabricManager class
        mock_manager = MagicMock()
        mock_manager.list_instances.return_value = []
        
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
                    assert isinstance(result, dict)
                    assert 'instances' in result

    def test_powerbi_module_load(self):
        """Test that the powerbi module can be loaded"""
        # Mock the PowerBIManager class
        mock_manager = MagicMock()
        mock_manager.list_premium_instances.return_value = []
        
        # Mock the _powerbi_manager global variable
        with patch('modules.powerbi._powerbi_manager', None):
            # Mock initialize_credential to avoid actual authentication
            with patch('modules.powerbi.initialize_credential', return_value=MagicMock()):
                # Mock PowerBIManager to return our mock manager
                with patch('modules.powerbi.PowerBIManager', return_value=mock_manager):
                    # Call load_and_run with the powerbi module
                    result = load_and_run(
                        'modules.powerbi',
                        {'subscription_id': 'test-subscription', 'resource_group': 'test-rg'},
                        'list'
                    )
                    
                    # Verify that the manager's list_premium_instances method was called
                    mock_manager.list_premium_instances.assert_called_once_with('test-rg')
                    
                    # Verify the result structure
                    assert isinstance(result, dict)
                    assert 'instances' in result

    def test_module_run_with_defaults(self):
        """Test running a module with default run method"""
        # Mock the module with multiple functions
        mock_module = MagicMock()
        mock_module.run.return_value = {"result": "default operation"}
        mock_module.list.return_value = {"result": "list operation"}
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            # Call load_and_run without specifying a command
            result = load_and_run('test_module', {'arg1': 'value1'})
            
            # Verify the run function was called (default)
            mock_module.run.assert_called_once_with(arg1='value1')
            
            # Verify the list function was not called
            mock_module.list.assert_not_called()
            
            # Verify the result is correct
            assert result == {"result": "default operation"}
