#!/usr/bin/env python3
"""
Unit tests for MySQL Database and User Management Script
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import mysql.connector
from mysql.connector import Error
import sys
import os

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our MySQL manager (assuming the main script is named mysql_manager.py)
try:
    from mysql_manager import MySQLManager
except ImportError:
    # If running from the same directory
    import mysql_manager
    MySQLManager = mysql_manager.MySQLManager


class TestMySQLManager:
    """Test cases for MySQLManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.manager = MySQLManager(
            host='test_host',
            port=3306,
            admin_user='test_admin',
            admin_password='test_password'
        )
    
    @patch('mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful MySQL connection."""
        # Mock connection object
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        result = self.manager.connect()
        
        assert result is True
        assert self.manager.connection == mock_connection
        mock_connect.assert_called_once_with(
            host='test_host',
            port=3306,
            user='test_admin',
            password='test_password',
            autocommit=True
        )
    
    @patch('mysql.connector.connect')
    def test_connect_failure(self, mock_connect):
        """Test MySQL connection failure."""
        mock_connect.side_effect = Error("Connection failed")
        
        result = self.manager.connect()
        
        assert result is False
        assert self.manager.connection is None
    
    @patch('getpass.getpass')
    @patch('mysql.connector.connect')
    def test_connect_with_password_prompt(self, mock_connect, mock_getpass):
        """Test connection with password prompt."""
        # Setup manager without password
        self.manager.admin_password = None
        mock_getpass.return_value = 'prompted_password'
        
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        result = self.manager.connect()
        
        assert result is True
        mock_getpass.assert_called_once()
        mock_connect.assert_called_once_with(
            host='test_host',
            port=3306,
            user='test_admin',
            password='prompted_password',
            autocommit=True
        )
    
    def test_disconnect(self):
        """Test MySQL disconnection."""
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        self.manager.connection = mock_connection
        
        self.manager.disconnect()
        
        mock_connection.close.assert_called_once()
    
    def test_disconnect_no_connection(self):
        """Test disconnection when no connection exists."""
        self.manager.connection = None
        
        # Should not raise any exceptions
        self.manager.disconnect()
    
    def test_database_exists_true(self):
        """Test database exists check when database exists."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('test_db',)
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.database_exists('test_db')
        
        assert result is True
        mock_cursor.execute.assert_called_once_with("SHOW DATABASES LIKE 'test_db'")
        mock_cursor.close.assert_called_once()
    
    def test_database_exists_false(self):
        """Test database exists check when database doesn't exist."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.database_exists('test_db')
        
        assert result is False
    
    def test_database_exists_error(self):
        """Test database exists check with database error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Error("Database error")
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.database_exists('test_db')
        
        assert result is False
    
    def test_user_exists_true(self):
        """Test user exists check when user exists."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('test_user',)
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.user_exists('test_user', 'localhost')
        
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT User FROM mysql.user WHERE User = %s AND Host = %s",
            ('test_user', 'localhost')
        )
    
    def test_user_exists_false(self):
        """Test user exists check when user doesn't exist."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.user_exists('test_user')
        
        assert result is False
    
    @patch.object(MySQLManager, 'database_exists')
    def test_create_database_new(self, mock_db_exists):
        """Test creating a new database."""
        mock_db_exists.return_value = False
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.create_database('test_db')
        
        assert result is True
        expected_query = (
            "CREATE DATABASE test_db "
            "CHARACTER SET utf8mb4 "
            "COLLATE utf8mb4_unicode_ci"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)
        mock_cursor.close.assert_called_once()
    
    @patch.object(MySQLManager, 'database_exists')
    def test_create_database_exists(self, mock_db_exists):
        """Test creating a database that already exists."""
        mock_db_exists.return_value = True
        
        result = self.manager.create_database('test_db')
        
        assert result is True
    
    @patch.object(MySQLManager, 'database_exists')
    def test_create_database_error(self, mock_db_exists):
        """Test database creation with error."""
        mock_db_exists.return_value = False
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Error("Create database error")
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.create_database('test_db')
        
        assert result is False
    
    @patch.object(MySQLManager, 'user_exists')
    def test_create_user_new(self, mock_user_exists):
        """Test creating a new user."""
        mock_user_exists.return_value = False
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        success, password = self.manager.create_user('test_user', 'test_password')
        
        assert success is True
        assert password == 'test_password'
        mock_cursor.execute.assert_called_once_with(
            "CREATE USER 'test_user'@'%' IDENTIFIED BY %s",
            ('test_password',)
        )
    
    @patch.object(MySQLManager, 'user_exists')
    @patch.object(MySQLManager, 'generate_password')
    def test_create_user_generated_password(self, mock_gen_password, mock_user_exists):
        """Test creating a user with generated password."""
        mock_user_exists.return_value = False
        mock_gen_password.return_value = 'generated_password'
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        success, password = self.manager.create_user('test_user')
        
        assert success is True
        assert password == 'generated_password'
        mock_gen_password.assert_called_once()
    
    @patch.object(MySQLManager, 'user_exists')
    def test_create_user_exists(self, mock_user_exists):
        """Test creating a user that already exists."""
        mock_user_exists.return_value = True
        
        success, password = self.manager.create_user('test_user', 'test_password')
        
        assert success is True
        assert password == 'test_password'
    
    def test_grant_privileges_success(self):
        """Test granting privileges successfully."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.grant_privileges('test_user', 'test_db')
        
        assert result is True
        expected_calls = [
            mock.call("GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'%'"),
            mock.call("FLUSH PRIVILEGES")
        ]
        mock_cursor.execute.assert_has_calls(expected_calls)
    
    def test_grant_privileges_error(self):
        """Test granting privileges with error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Error("Grant error")
        mock_connection.cursor.return_value = mock_cursor
        self.manager.connection = mock_connection
        
        result = self.manager.grant_privileges('test_user', 'test_db')
        
        assert result is False
    
    @patch.object(MySQLManager, 'create_database')
    @patch.object(MySQLManager, 'create_user')
    @patch.object(MySQLManager, 'grant_privileges')
    def test_setup_database_and_user_success(self, mock_grant, mock_create_user, mock_create_db):
        """Test complete setup success."""
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        self.manager.connection = mock_connection
        
        mock_create_db.return_value = True
        mock_create_user.return_value = (True, 'generated_password')
        mock_grant.return_value = True
        
        result = self.manager.setup_database_and_user('test_db', 'test_user')
        
        assert result['success'] is True
        assert result['database'] == 'test_db'
        assert result['username'] == 'test_user'
        assert result['password'] == 'generated_password'
        assert result['host'] == '%'
        
        mock_create_db.assert_called_once_with('test_db')
        mock_create_user.assert_called_once_with('test_user', None, '%')
        mock_grant.assert_called_once_with('test_user', 'test_db', '%')
    
    @patch.object(MySQLManager, 'create_database')
    def test_setup_database_and_user_db_failure(self, mock_create_db):
        """Test setup with database creation failure."""
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        self.manager.connection = mock_connection
        
        mock_create_db.return_value = False
        
        result = self.manager.setup_database_and_user('test_db', 'test_user')
        
        assert result['success'] is False
        assert "Failed to create database 'test_db'" in result['messages']
    
    def test_setup_database_and_user_no_connection(self):
        """Test setup without connection."""
        self.manager.connection = None
        
        result = self.manager.setup_database_and_user('test_db', 'test_user')
        
        assert result['success'] is False
        assert "Not connected to MySQL server" in result['messages']
    
    def test_generate_password(self):
        """Test password generation."""
        password = MySQLManager.generate_password(16)
        
        assert len(password) == 16
        assert isinstance(password, str)
        
        # Test different length
        password_short = MySQLManager.generate_password(8)
        assert len(password_short) == 8
        
        # Test that passwords are different
        password2 = MySQLManager.generate_password(16)
        assert password != password2


class TestMySQLManagerIntegration:
    """Integration tests that could be run against a real MySQL instance."""
    
    @pytest.mark.skip(reason="Requires actual MySQL instance")
    def test_real_connection(self):
        """Test connection to a real MySQL instance."""
        # This test would require a real MySQL instance
        # Uncomment and modify for actual integration testing
        manager = MySQLManager(
            host='localhost',
            port=3306,
            admin_user='root',
            admin_password='password'
        )
        
        assert manager.connect() is True
        manager.disconnect()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
