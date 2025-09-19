# mysql-db-with-user
# MySQL Database and User Management Tool

A Python script for automating MySQL database and user creation with full privilege assignment. Designed specifically for MySQL servers running in Docker deployments.

## 🚀 Features

- **Database Creation**: Create new MySQL databases with custom character sets and collations
- **User Management**: Create MySQL users with secure password generation
- **Privilege Assignment**: Grant full privileges to users on specific databases
- **Docker Compatible**: Works seamlessly with MySQL running in Docker containers
- **Security Focused**: Secure password generation and proper connection handling
- **Comprehensive Testing**: Full unit test coverage with pytest
- **Error Handling**: Robust error handling and logging
- **CLI Interface**: Easy-to-use command-line interface
- **Flexible Configuration**: Support for various MySQL configurations

## 📋 Prerequisites

- Python 3.7 or higher
- MySQL server (can be running in Docker)
- Admin access to MySQL server

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mysql-manager.git
   cd mysql-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install mysql-connector-python pytest
   ```

3. **Make the script executable:**
   ```bash
   chmod +x mysql_manager.py
   ```

## 📦 Docker MySQL Setup

If you're running MySQL in Docker, here's a quick setup:

```bash
# Start MySQL container
docker run --name mysql-server -e MYSQL_ROOT_PASSWORD=yourpassword -p 3306:3306 -d mysql:8.0

# Wait for MySQL to be ready
docker logs mysql-server

# Test connection
docker exec -it mysql-server mysql -uroot -p
```

## 🚀 Usage

### Basic Usage

Create a database and user with generated password:

```bash
python mysql_manager.py myapp_db myapp_user
```

### Advanced Usage

```bash
# Specify MySQL host and port
python mysql_manager.py myapp_db myapp_user --host localhost --port 3306

# Use custom admin credentials
python mysql_manager.py myapp_db myapp_user --admin-user root --admin-password mypassword

# Set custom user password
python mysql_manager.py myapp_db myapp_user --user-password myuserpassword

# Restrict user to specific host
python mysql_manager.py myapp_db myapp_user --user-host localhost

# Enable verbose logging
python mysql_manager.py myapp_db myapp_user --verbose
```

### Example Output

```
✅ Setup completed successfully!
Database: myapp_db
Username: myapp_user  
Password: A3k9$mN7@pQx2zL8
Host: %

Connection string:
mysql://myapp_user:A3k9$mN7@pQx2zL8@localhost:3306/myapp_db
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `database` | Database name to create | Required |
| `username` | Username to create | Required |
| `--host` | MySQL host | localhost |
| `--port` | MySQL port | 3306 |
| `--admin-user` | Admin username | root |
| `--admin-password` | Admin password | Prompted if not provided |
| `--user-password` | Password for new user | Auto-generated |
| `--user-host` | Host for new user | % (all hosts) |
| `--verbose` | Enable verbose logging | False |

## 🐍 Python API Usage

You can also use the MySQLManager class directly in your Python code:

```python
from mysql_manager import MySQLManager

# Initialize manager
manager = MySQLManager(
    host='localhost',
    port=3306,
    admin_user='root',
    admin_password='admin_password'
)

# Connect to MySQL
if manager.connect():
    # Create database and user
    result = manager.setup_database_and_user(
        database_name='myapp_db',
        username='myapp_user',
        password='custom_password'  # Optional
    )
    
    if result['success']:
        print(f"Database: {result['database']}")
        print(f"Username: {result['username']}")
        print(f"Password: {result['password']}")
    else:
        print("Setup failed:", result['messages'])
    
    manager.disconnect()
```

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest test_mysql_manager.py -v

# Run with coverage
pip install pytest-cov
pytest test_mysql_manager.py --cov=mysql_manager --cov-report=html

# Run specific test
pytest test_mysql_manager.py::TestMySQLManager::test_connect_success -v
```

### Test Structure

```
tests/
├── test_mysql_manager.py      # Unit tests
├── conftest.py               # Pytest configuration
└── integration/              # Integration tests (require real DB)
    └── test_integration.py
```

## 🐳 Docker Integration Examples

### Using with Docker Compose

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  app:
    build: .
    depends_on:
      - mysql
    environment:
      DB_HOST: mysql
      DB_PORT: 3306
    command: python mysql_manager.py myapp_db myapp_user --host mysql

volumes:
  mysql_data:
```

### Docker Network Usage

```bash
# Create a Docker network
docker network create mysql-network

# Run MySQL in the network
docker run --name mysql-server --network mysql-network \
  -e MYSQL_ROOT_PASSWORD=rootpassword -d mysql:8.0

# Run the script in the same network
docker run --network mysql-network -it \
  -v $(pwd):/app python:3.9 \
  python /app/mysql_manager.py myapp_db myapp_user --host mysql-server
```

## 🔒 Security Considerations

- **Password Security**: Generated passwords use cryptographically secure random generation
- **Connection Security**: Use SSL connections in production environments
- **Privilege Principle**: Consider using more restrictive privileges instead of `ALL PRIVILEGES` for production
- **Network Security**: Restrict MySQL access to specific hosts when possible
- **Environment Variables**: Store sensitive credentials in environment variables

### Environment Variable Support

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_ADMIN_USER=root
export MYSQL_ADMIN_PASSWORD=secret

python mysql_manager.py myapp_db myapp_user
```

## 📁 Project Structure

```
mysql-manager/
├── mysql_manager.py          # Main script
├── test_mysql_manager.py     # Unit tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── LICENSE                   # License file
└── examples/                 # Usage examples
    ├── docker-compose.yml
    └── kubernetes.yaml
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/mysql-manager.git
cd mysql-manager

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📝 Requirements Files

### requirements.txt
```
mysql-connector-python>=8.0.0
```

### requirements-dev.txt
```
mysql-connector-python>=8.0.0
pytest>=6.0.0
pytest-cov>=2.10.0
pytest-mock>=3.6.0
black>=22.0.0
flake8>=4.0.0
pre-commit>=2.15.0
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Can't connect to MySQL server
   ```
   - Verify MySQL is running: `docker ps` or `systemctl status mysql`
   - Check host and port settings
   - Verify firewall settings

2. **Access Denied**
   ```
   Error: Access denied for user 'root'@'localhost'
   ```
   - Verify admin credentials
   - Check MySQL user permissions
   - Ensure user has CREATE privilege

3. **Database Already Exists**
   ```
   Warning: Database 'myapp_db' already exists
   ```
   - This is normal behavior; the script continues
   - Use different database name if needed

4. **Docker Permission Issues**
   ```
   Error: Permission denied
   ```
   - Run with `sudo` if necessary
   - Check Docker daemon status
   - Verify user is in docker group

### Debug Mode

Enable debug logging for troubleshooting:

```bash
python mysql_manager.py myapp_db myapp_user --verbose
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/) for database connectivity
- [pytest](https://pytest.org/) for testing framework
- [Docker](https://www.docker.com/) for containerization support

## 📊 Project Status

![Tests](https://github.com/yourusername/mysql-manager/workflows/tests/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MySQL](https://img.shields.io/badge/mysql-5.7%2B%20%7C%208.0%2B-orange)

---

**Need help?** Open an issue or check our [documentation](https://github.com/yourusername/mysql-manager/wiki).
