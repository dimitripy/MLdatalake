import unittest
from unittest.mock import patch, MagicMock
import importlib
import os
import json
import sys
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from dags.modules.SQLAlchemy_functions import start_session, Base, insert_data, load_config, create_db_engine

# Import the functions and classes to be tested

class TestSQLAlchemyFunctions(unittest.TestCase):

    @patch('dags.modules.SQLAlchemy_functions.load_config')
    @patch('dags.modules.SQLAlchemy_functions.create_db_engine')
    @patch('dags.modules.SQLAlchemy_functions.Base.metadata.create_all')
    @patch('dags.modules.SQLAlchemy_functions.sessionmaker')
    def test_start_session_success(self, mock_sessionmaker, mock_create_all, mock_create_db_engine, mock_load_config):
        # Mock the configuration
        mock_load_config.return_value = {
            'db_user': 'user',
            'db_password': 'password',
            'db_host': 'localhost',
            'db_port': '3306',
            'db_name': 'test_db'
        }
        
        # Mock the session
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session
        
        # Call the function
        session = start_session(config_path='dummy_path')
        
        # Assertions
        mock_load_config.assert_called_once_with('dummy_path')
        mock_create_db_engine.assert_called_once()
        mock_create_all.assert_called_once()
        mock_sessionmaker.assert_called_once()
        self.assertIsNotNone(session)

    @patch('dags.modules.SQLAlchemy_functions.load_config')
    @patch('dags.modules.SQLAlchemy_functions.create_db_engine')
    @patch('dags.modules.SQLAlchemy_functions.Base.metadata.create_all')
    @patch('dags.modules.SQLAlchemy_functions.sessionmaker')
    def test_start_session_failure_loading_config(self, mock_sessionmaker, mock_create_all, mock_create_db_engine, mock_load_config):
        # Mock load_config to raise an exception
        mock_load_config.side_effect = Exception("Error loading config")
        
        # Call the function
        session = start_session(config_path='dummy_path')
        
        # Assertions
        mock_load_config.assert_called_once_with('dummy_path')
        mock_create_db_engine.assert_not_called()
        mock_create_all.assert_not_called()
        mock_sessionmaker.assert_not_called()
        self.assertIsNone(session)

    @patch('dags.modules.SQLAlchemy_functions.load_config')
    @patch('dags.modules.SQLAlchemy_functions.create_db_engine')
    @patch('dags.modules.SQLAlchemy_functions.Base.metadata.create_all')
    @patch('dags.modules.SQLAlchemy_functions.sessionmaker')
    def test_start_session_failure_creating_engine(self, mock_sessionmaker, mock_create_all, mock_create_db_engine, mock_load_config):
        # Mock the configuration
        mock_load_config.return_value = {
            'db_user': 'user',
            'db_password': 'password',
            'db_host': 'localhost',
            'db_port': '3306',
            'db_name': 'test_db'
        }
        
        # Mock create_db_engine to raise an exception
        mock_create_db_engine.side_effect = SQLAlchemyError("Error creating engine")
        
        # Call the function
        session = start_session(config_path='dummy_path')
        
        # Assertions
        mock_load_config.assert_called_once_with('dummy_path')
        mock_create_db_engine.assert_called_once()
        mock_create_all.assert_not_called()
        mock_sessionmaker.assert_not_called()
        self.assertIsNone(session)

    @patch('os.path.abspath')
    @patch('os.path.dirname')
    def test_start_session_default_config_path(self, mock_dirname, mock_abspath):
        # Mock os.path functions
        mock_dirname.return_value = '/dummy_dir'
        mock_abspath.return_value = '/dummy_dir/config.json'
        
        with patch('dags.modules.SQLAlchemy_functions.load_config') as mock_load_config, \
             patch('dags.modules.SQLAlchemy_functions.create_db_engine'), \
             patch('dags.modules.SQLAlchemy_functions.Base.metadata.create_all'), \
             patch('dags.modules.SQLAlchemy_functions.sessionmaker'):
            
            # Call the function without config_path
            start_session()
            
            # Assertions
            mock_abspath.assert_called_once_with('/dummy_dir/config.json')
            mock_load_config.assert_called_once_with('/dummy_dir/config.json')
    
    '''    @patch('dags.modules.SQLAlchemy_functions.subprocess.check_call')
    @patch('importlib.import_module')
    def test_install_dependencies(self, mock_import, mock_check_call):
        # Mock import_module to raise ImportError for the first package
        mock_import.side_effect = [ImportError, lambda name, *args: importlib.import_module(name, *args)]
        
        from dags.modules.SQLAlchemy_functions import install_dependencies
        install_dependencies()
        
        # Assertions
        mock_import.assert_any_call("pymysql")
        mock_import.assert_any_call("cryptography")
        mock_check_call.assert_called_once_with([sys.executable, "-m", "pip", "install", "pymysql"])'''

    @patch('dags.modules.SQLAlchemy_functions.sessionmaker')
    def test_insert_data(self, mock_sessionmaker):
        # Mock session and data
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session
        data = pd.DataFrame({
            'date': ['2023-01-01'],
            'open': [100.0],
            'high': [110.0],
            'low': [90.0],
            'close': [105.0],
            'volume': [1000.0]
        })
        
        from dags.modules.SQLAlchemy_functions import MinuteBar
        insert_data(mock_session, data, MinuteBar, 1)
        
        # Assertions
        self.assertEqual(mock_session.add.call_count, 1)
        mock_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()