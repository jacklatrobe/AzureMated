"""
Tests for the main.py application
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from utils.module_loader import load_and_run


class TestMainApplication:
    """Test class for main.py application"""

    def test_run_module_success(self):
        """Test run_module function with successful execution"""
        # Create mock args
        mock_args = MagicMock()
        mock_args.module_name = "test_module"
        mock_args.command = "list"
        mock_args.__dict__ = {
            "module_name": "test_module",
            "command": "list",
            "subscription_id": "test-subscription",
            "func": MagicMock()
        }
        
        # Mock load_and_run to return a success result
        with patch('main.load_and_run', return_value={"result": "success"}):
            # Mock console.print to avoid printing during tests
            with patch('main.console.print'):
                # Call the function
                main.run_module(mock_args)
                
                # Verify load_and_run was called with correct arguments
                main.load_and_run.assert_called_once_with(
                    "modules.test_module",
                    {"subscription_id": "test-subscription"},
                    "list"
                )

    def test_run_module_without_command(self):
        """Test run_module function without a specific command"""
        # Create mock args without a command
        mock_args = MagicMock()
        mock_args.module_name = "test_module"
        mock_args.command = None
        mock_args.__dict__ = {
            "module_name": "test_module",
            "subscription_id": "test-subscription",
            "func": MagicMock()
        }
        
        # Mock load_and_run to return a success result
        with patch('main.load_and_run', return_value={"result": "success"}):
            # Mock console.print to avoid printing during tests
            with patch('main.console.print'):
                # Call the function
                main.run_module(mock_args)
                
                # Verify load_and_run was called with correct arguments
                main.load_and_run.assert_called_once_with(
                    "modules.test_module",
                    {"subscription_id": "test-subscription"},
                    None
                )

    def test_run_module_error(self):
        """Test run_module function with an error"""
        # Create mock args
        mock_args = MagicMock()
        mock_args.module_name = "test_module"
        mock_args.command = "list"
        mock_args.__dict__ = {
            "module_name": "test_module",
            "command": "list",
            "subscription_id": "test-subscription",
            "func": MagicMock()
        }
        
        # Mock load_and_run to raise an exception
        with patch('main.load_and_run', side_effect=ValueError("Test error")):
            # Mock console.print to avoid printing during tests
            with patch('main.console.print'):
                # Mock sys.exit to avoid exiting the test
                with patch('main.sys.exit'):
                    # Call the function
                    main.run_module(mock_args)
                    
                    # Verify sys.exit was called with exit code 1
                    main.sys.exit.assert_called_once_with(1)

    def test_main_with_module_command(self):
        """Test main function with a module and command"""
        # Mock argparse.ArgumentParser to avoid actual CLI parsing
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.module_name = "fabric"
        mock_args.command = "list"
        
        # Setup the parser to return our mock args
        mock_parser.parse_args.return_value = mock_args
        
        # Mock run_module to avoid actual execution
        with patch('main.argparse.ArgumentParser', return_value=mock_parser):
            with patch('main.run_module') as mock_run_module:
                with patch('main.console.print'):
                    # Call the function
                    main.main()
                    
                    # Verify run_module was called with the correct args
                    mock_run_module.assert_called_once_with(mock_args)

    def test_main_without_module(self):
        """Test main function without a module (should show help)"""
        # Mock argparse.ArgumentParser to avoid actual CLI parsing
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.module_name = None
        
        # Setup the parser to return our mock args
        mock_parser.parse_args.return_value = mock_args
        
        # Mock run_module to avoid actual execution
        with patch('main.argparse.ArgumentParser', return_value=mock_parser):
            with patch('main.console.print'):
                # Call the function
                main.main()
                
                # Verify print_help was called
                mock_parser.print_help.assert_called_once()
