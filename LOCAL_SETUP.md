# 🏠 Real Estate Data Pipeline - Local Setup Guide

This guide will help you run the Real Estate Data Pipeline project on your local machine.

## 📋 Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## 🚀 Quick Start (Recommended)

### Option 1: Using Docker Compose (Easiest)

1. **Navigate to the project directory**
   ```bash
   cd real_estate_pipeline
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

5. **Test the API**
   ```bash
   # Get all properties
   curl http://localhost:8000/api/v1/properties
   
   # Trigger data collection (demo data)
   curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA"
   ```

### Option 2: Local Development Setup

1. **Install Python dependencies**
   ```bash
   cd real_estate_pipeline
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**
   
   **Using Docker for databases only:**
   ```bash
   # Start only PostgreSQL and Redis
   docker-compose up -d postgres redis
   ```
   
   **Or install locally:**
   - Install PostgreSQL and create database `real_estate_db`
   - Install Redis server

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

4. **Run the application**
   ```bash
   # Start the FastAPI server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## 🧪 Testing the Setup

### Run the Demo Script

```bash
cd real_estate_pipeline
python demo_script.py
```

This will demonstrate:
- Data collection simulation
- Data processing pipeline
- Analytics capabilities
- API usage examples

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get properties
curl http://localhost:8000/api/v1/properties

# Get market trends
curl "http://localhost:8000/api/v1/analytics/market-trends?city=San Francisco"

# View available data sources
curl http://localhost:8000/api/v1/data/sources
```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/real_estate_db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# API Keys (optional for demo)
RENTSPIDER_API_KEY=your_api_key_here
REALTYMOLE_API_KEY=your_api_key_here

# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
LOG_LEVEL=INFO
```

### API Keys (Optional)

For production use, you'll need API keys from:
- [RentSpider API](https://rentspider.com/api)
- [RealtyMole API](https://rapidapi.com/realtymole/api/realtymole-rental-estimate-v1)

**Note:** The demo works without real API keys using sample data.

## 📊 Using the System

### 1. View API Documentation
Open http://localhost:8000/docs in your browser to see interactive API documentation.

### 2. Collect Data
```bash
# Trigger data collection for a city
curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA&sources=rentspider"
```

### 3. Query Properties
```bash
# Get properties with filters
curl "http://localhost:8000/api/v1/properties?city=San Francisco&min_price=500000&max_price=1000000"
```

### 4. Get Analytics
```bash
# Market trends
curl "http://localhost:8000/api/v1/analytics/market-trends?city=San Francisco&state=CA"
```

## 🛠️ Development Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Rebuild containers
docker-compose build --no-cache
```

### Database Commands
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d real_estate_db

# View tables
\dt

# Exit PostgreSQL
\q
```

### Python Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (when implemented)
pytest

# Format code
black .

# Run linting
flake8
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **Database connection error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Permission denied errors**
   ```bash
   # Fix file permissions
   chmod +x setup.py demo_script.py
   ```

4. **Python import errors**
   ```bash
   # Make sure you're in the project directory
   cd real_estate_pipeline
   
   # Install dependencies
   pip install -r requirements.txt
   ```

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f api

# View all service logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## 📱 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |
| GET | `/api/v1/properties` | List properties |
| GET | `/api/v1/properties/{id}` | Get property details |
| POST | `/api/v1/data/collect` | Trigger data collection |
| GET | `/api/v1/analytics/market-trends` | Market analytics |
| GET | `/api/v1/data/sources` | Available data sources |

## 🎯 Next Steps

1. **Add Real API Keys**: Update `.env` with actual API keys for live data
2. **Customize Collectors**: Add more data sources in `collectors/` directory
3. **Extend Analytics**: Add more analytics endpoints
4. **Add Authentication**: Implement user authentication for production
5. **Scale Up**: Use Docker Swarm or Kubernetes for production deployment

## 💡 Tips

- Use the interactive API docs at `/docs` to test endpoints
- Check logs regularly for debugging: `docker-compose logs -f`
- The demo script shows all major functionality without needing real API keys
- Start with Docker Compose for the easiest setup experience

## 🆘 Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs -f api`
2. Verify services are running: `docker-compose ps`
3. Review the troubleshooting section above
4. Check the main README.md for additional information

---

**Happy coding! 🚀**