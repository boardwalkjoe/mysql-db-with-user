#!/usr/bin/env python3
"""
MySQL Database and User Management Script

This script creates a new MySQL database and assigns a user with full privileges.
Designed to work with MySQL servers running in Docker deployments.
"""

import sys
import argparse
import logging
import getpass
from typing import Optional, Dict, Any
import mysql.connector
from mysql.connector import Error
import secrets
import string


class MySQLManager:
    """Manages MySQL database and user operations."""
    
    def __init__(self, host: str = 'localhost', port: int = 3306, 
                 admin_user: str = 'root', admin_password: str = None):
        """
        Initialize MySQL Manager.
        
        Args:
            host: MySQL server host
            port: MySQL server port
            admin_user: Admin username for MySQL
            admin_password: Admin password for MySQL
        """
        self.host = host
        self.port = port
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.connection = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Establish connection to MySQL server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self.admin_password:
                self.admin_password = getpass.getpass(f"Enter password for {self.admin_user}: ")
            
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.admin_user,
                password=self.admin_password,
                autocommit=True
            )
            
            if self.connection.is_connected():
                self.logger.info(f"Successfully connected to MySQL server at {self.host}:{self.port}")
                return True
                
        except Error as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            return False
        
        return False
    
    def disconnect(self):
        """Close MySQL connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("MySQL connection closed")
    
    def database_exists(self, database_name: str) -> bool:
        """
        Check if database exists.
        
        Args:
            database_name: Name of the database to check
            
        Returns:
            bool: True if database exists, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            self.logger.error(f"Error checking database existence: {e}")
            return False
    
    def user_exists(self, username: str, host: str = '%') -> bool:
        """
        Check if user exists.
        
        Args:
            username: Username to check
            host: Host for the user (default: '%' for all hosts)
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT User FROM mysql.user WHERE User = %s AND Host = %s",
                (username, host)
            )
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            self.logger.error(f"Error checking user existence: {e}")
            return False
    
    def create_database(self, database_name: str, charset: str = 'utf8mb4', 
                       collation: str = 'utf8mb4_unicode_ci') -> bool:
        """
        Create a new database.
        
        Args:
            database_name: Name of the database to create
            charset: Character set for the database
            collation: Collation for the database
            
        Returns:
            bool: True if database created successfully, False otherwise
        """
        try:
            if self.database_exists(database_name):
                self.logger.warning(f"Database '{database_name}' already exists")
                return True
            
            cursor = self.connection.cursor()
            create_db_query = (
                f"CREATE DATABASE {database_name} "
                f"CHARACTER SET {charset} "
                f"COLLATE {collation}"
            )
            cursor.execute(create_db_query)
            cursor.close()
            
            self.logger.info(f"Database '{database_name}' created successfully")
            return True
            
        except Error as e:
            self.logger.error(f"Error creating database '{database_name}': {e}")
            return False
    
    def create_user(self, username: str, password: str = None, 
                   host: str = '%') -> tuple[bool, str]:
        """
        Create a new MySQL user.
        
        Args:
            username: Username for the new user
            password: Password for the new user (generated if None)
            host: Host for the user (default: '%' for all hosts)
            
        Returns:
            tuple: (success: bool, password: str)
        """
        try:
            if self.user_exists(username, host):
                self.logger.warning(f"User '{username}'@'{host}' already exists")
                return True, password
            
            # Generate secure password if not provided
            if not password:
                password = self.generate_password()
            
            cursor = self.connection.cursor()
            create_user_query = f"CREATE USER '{username}'@'{host}' IDENTIFIED BY %s"
            cursor.execute(create_user_query, (password,))
            cursor.close()
            
            self.logger.info(f"User '{username}'@'{host}' created successfully")
            return True, password
            
        except Error as e:
            self.logger.error(f"Error creating user '{username}'@'{host}': {e}")
            return False, password
    
    def grant_privileges(self, username: str, database_name: str, 
                        host: str = '%', privileges: str = 'ALL PRIVILEGES') -> bool:
        """
        Grant privileges to a user on a database.
        
        Args:
            username: Username to grant privileges to
            database_name: Database name
            host: Host for the user
            privileges: Privileges to grant (default: 'ALL PRIVILEGES')
            
        Returns:
            bool: True if privileges granted successfully, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            grant_query = (
                f"GRANT {privileges} ON {database_name}.* "
                f"TO '{username}'@'{host}'"
            )
            cursor.execute(grant_query)
            cursor.execute("FLUSH PRIVILEGES")
            cursor.close()
            
            self.logger.info(
                f"Granted {privileges} on '{database_name}' to '{username}'@'{host}'"
            )
            return True
            
        except Error as e:
            self.logger.error(
                f"Error granting privileges to '{username}'@'{host}': {e}"
            )
            return False
    
    def setup_database_and_user(self, database_name: str, username: str, 
                               password: str = None, host: str = '%') -> Dict[str, Any]:
        """
        Complete setup: create database, create user, and grant privileges.
        
        Args:
            database_name: Name of the database to create
            username: Username for the new user
            password: Password for the new user (generated if None)
            host: Host for the user
            
        Returns:
            dict: Setup results with success status, username, password, and database
        """
        result = {
            'success': False,
            'database': database_name,
            'username': username,
            'password': None,
            'host': host,
            'messages': []
        }
        
        if not self.connection or not self.connection.is_connected():
            result['messages'].append("Not connected to MySQL server")
            return result
        
        # Create database
        if not self.create_database(database_name):
            result['messages'].append(f"Failed to create database '{database_name}'")
            return result
        
        # Create user
        user_success, user_password = self.create_user(username, password, host)
        if not user_success:
            result['messages'].append(f"Failed to create user '{username}'@'{host}'")
            return result
        
        result['password'] = user_password
        
        # Grant privileges
        if not self.grant_privileges(username, database_name, host):
            result['messages'].append(
                f"Failed to grant privileges to '{username}'@'{host}'"
            )
            return result
        
        result['success'] = True
        result['messages'].append("Database and user setup completed successfully")
        return result
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of the password
            
        Returns:
            str: Generated password
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password


def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(
        description="Create MySQL database and user with full privileges"
    )
    parser.add_argument('database', help='Database name to create')
    parser.add_argument('username', help='Username to create')
    parser.add_argument('--host', default='localhost', help='MySQL host (default: localhost)')
    parser.add_argument('--port', type=int, default=3306, help='MySQL port (default: 3306)')
    parser.add_argument('--admin-user', default='root', help='Admin username (default: root)')
    parser.add_argument('--admin-password', help='Admin password (will prompt if not provided)')
    parser.add_argument('--user-password', help='Password for new user (generated if not provided)')
    parser.add_argument('--user-host', default='%', help='Host for new user (default: %)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create MySQL manager
    manager = MySQLManager(
        host=args.host,
        port=args.port,
        admin_user=args.admin_user,
        admin_password=args.admin_password
    )
    
    try:
        # Connect to MySQL
        if not manager.connect():
            print("Failed to connect to MySQL server")
            sys.exit(1)
        
        # Setup database and user
        result = manager.setup_database_and_user(
            database_name=args.database,
            username=args.username,
            password=args.user_password,
            host=args.user_host
        )
        
        # Display results
        if result['success']:
            print(f"\n✅ Setup completed successfully!")
            print(f"Database: {result['database']}")
            print(f"Username: {result['username']}")
            print(f"Password: {result['password']}")
            print(f"Host: {result['host']}")
            print(f"\nConnection string:")
            print(f"mysql://{result['username']}:{result['password']}@{args.host}:{args.port}/{result['database']}")
        else:
            print(f"\n❌ Setup failed!")
            for message in result['messages']:
                print(f"  - {message}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()
