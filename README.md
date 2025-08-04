# IP Reversal Web Application

A modern web application built with FastAPI and PostgreSQL that displays the origin public IP address of requests in reverse format and stores them in a database.

## Features

- 🌐 **Web Interface**: Beautiful, responsive web page showing your reversed IP address
- 🔌 **REST API**: Full API with automatic documentation (Swagger/OpenAPI)
- 💾 **Database Storage**: PostgreSQL database storing all IP addresses with timestamps
- 📊 **Statistics**: Real-time application statistics and IP history
- 🏥 **Health Checks**: Built-in health monitoring endpoints
- 🐳 **Docker Ready**: Complete containerization setup for development and production
- 🔒 **Security**: Proper error handling and input validation

## Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Templates**: Jinja2
- **Containerization**: Docker & Docker Compose
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd K8S PROJECT
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/api/health

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. **Start PostgreSQL** (using Docker)
   ```bash
   docker run -d --name postgres \
     -e POSTGRES_DB=ip_reversal_db \
     -e POSTGRES_USER=user \
     -e POSTGRES_PASSWORD=password \
     -p 5432:5432 \
     postgres:15-alpine
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface showing reversed IP |
| `GET` | `/api/ip` | Get reversed IP address (JSON) |
| `GET` | `/api/history` | Get IP address history |
| `GET` | `/api/stats` | Get application statistics |
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/docs` | Interactive API documentation |

### Example API Usage

```bash
# Get your reversed IP
curl http://localhost:8000/api/ip

# Get IP history (last 10 records)
curl "http://localhost:8000/api/history?limit=10"

# Get application statistics
curl http://localhost:8000/api/stats

# Health check
curl http://localhost:8000/api/health
```

## Project Structure

```
K8S PROJECT/
├── src/
│   ├── __init__.py
│   ├── api.py              # FastAPI application and routes
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database models and connection
│   ├── models.py           # Pydantic models
│   ├── services.py         # Business logic
│   ├── utils.py            # Utility functions
│   └── templates/          # HTML templates
│       ├── index.html      # Main web interface
│       └── error.html      # Error page
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── docker-compose.yml      # Local development setup
└── README.md              # This file
```

## Configuration

The application uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/ip_reversal_db` | Database connection string |
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality

```bash
# Install development tools
pip install black flake8 mypy

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Docker Commands

### Development

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production

```bash
# Build production image
docker build -t ip-reversal-app .

# Run production container
docker run -d \
  --name ip-reversal-app \
  -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  ip-reversal-app
```

## Database Schema

The application uses a single table `ip_addresses`:

```sql
CREATE TABLE ip_addresses (
    id SERIAL PRIMARY KEY,
    original_ip VARCHAR(45) NOT NULL,
    reversed_ip VARCHAR(45) NOT NULL,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Monitoring

The application includes several monitoring endpoints:

- **Health Check**: `/api/health` - Overall application health
- **Statistics**: `/api/stats` - Request counts and metrics
- **History**: `/api/history` - IP address history with pagination

## Security Considerations

- Input validation for all IP addresses
- SQL injection protection via SQLAlchemy ORM
- Proper error handling without exposing sensitive information
- Non-root user in Docker containers
- Health checks for container orchestration

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database URL in environment variables
   - Verify network connectivity

2. **Port Already in Use**
   - Change the port in docker-compose.yml or environment variables
   - Check if another service is using port 8000

3. **Permission Errors**
   - Ensure Docker has proper permissions
   - Check file ownership in mounted volumes

### Logs

```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at `/api/docs`
- Open an issue in the repository 