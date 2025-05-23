"""
Tests for the module_loader.py utility
"""

import importlib
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.module_loader import load_and_run


class TestModuleLoader:
    """Test class for module_loader.py"""

    def test_load_and_run_with_default_command(self):
        """Test that load_and_run correctly calls the run function of a module"""
        # Create a mock module with a run function
        mock_module = MagicMock()
        mock_module.run.return_value = {"result": "success"}
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            result = load_and_run('test_module', {'arg1': 'value1'})
            
            # Verify importlib.import_module was called with the correct module name
            importlib.import_module.assert_called_once_with('test_module')
            
            # Verify the run function was called with the correct arguments
            mock_module.run.assert_called_once_with(arg1='value1')
            
            # Verify the result is correct
            assert result == {"result": "success"}

    def test_load_and_run_with_specific_command(self):
        """Test that load_and_run correctly calls the specified command function of a module"""
        # Create a mock module with a command function
        mock_module = MagicMock()
        mock_module.list.return_value = {"items": ["item1", "item2"]}
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            result = load_and_run('test_module', {'arg1': 'value1'}, 'list')
            
            # Verify importlib.import_module was called with the correct module name
            importlib.import_module.assert_called_once_with('test_module')
            
            # Verify the list function was called with the correct arguments
            mock_module.list.assert_called_once_with(arg1='value1')
            
            # Verify the result is correct
            assert result == {"items": ["item1", "item2"]}

    def test_load_and_run_import_error(self):
        """Test that load_and_run raises ImportError when the module cannot be imported"""
        # Patch importlib.import_module to raise ImportError
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            with pytest.raises(ImportError, match="Module not found"):
                load_and_run('non_existent_module')

    def test_load_and_run_missing_function(self):
        """Test that load_and_run raises AttributeError when the function does not exist"""
        # Create a mock module without the requested function
        mock_module = MagicMock(spec=[])
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            with pytest.raises(AttributeError, match="does not have a run function"):
                load_and_run('test_module')

    def test_load_and_run_with_function_error(self):
        """Test that load_and_run properly handles errors in the module function"""
        # Create a mock module with a run function that raises an exception
        mock_module = MagicMock()
        mock_module.run.side_effect = ValueError("Test error")
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            with pytest.raises(ValueError, match="Test error"):
                load_and_run('test_module')
