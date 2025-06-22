# Real Estate Data Pipeline

A comprehensive real estate data collection and processing system that aggregates property data from multiple public APIs, processes it using Python/pandas, and stores it in PostgreSQL with a FastAPI interface.

## 🏗️ Architecture

This project implements a scalable data pipeline with the following components:

- **Data Collection**: Multi-source API integration with rate limiting and retry logic
- **Data Processing**: Pandas-based normalization, duplicate detection, and enrichment
- **Storage**: PostgreSQL database with optimized schema and indexing
- **API**: FastAPI with automatic documentation and real-time endpoints
- **Task Queue**: Celery for background processing with Redis broker
- **Containerization**: Docker and Docker Compose for easy deployment

## 🚀 Features

### Data Collection
- **Multi-source Integration**: RentSpider, RealtyMole, and extensible collector framework
- **Rate Limiting**: Intelligent rate limiting with exponential backoff
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Data Validation**: Schema validation and quality checks

### Data Processing
- **Normalization**: Address standardization, data type conversion, and field mapping
- **Duplicate Detection**: Fuzzy matching for addresses and property characteristics
- **Data Enrichment**: Calculated metrics, market segments, and investment scores
- **Geocoding**: Address-to-coordinate conversion for mapping

### API Features
- **RESTful Endpoints**: Full CRUD operations with filtering and pagination
- **Real-time Data**: Live property search and market analytics
- **Background Tasks**: Asynchronous data collection and processing
- **Auto Documentation**: OpenAPI/Swagger documentation

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd real_estate_pipeline
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Database: localhost:5432
   - Redis: localhost:6379

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**
   ```bash
   # Install PostgreSQL and Redis locally
   # Create database: real_estate_db
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Update database and Redis URLs in .env
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/real_estate_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Keys (obtain from respective providers)
RENTSPIDER_API_KEY=your_rentspider_api_key
REALTYMOLE_API_KEY=your_realtymole_api_key
ZILLOW_API_KEY=your_zillow_api_key
WALKSCORE_API_KEY=your_walkscore_api_key

# Application Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
LOG_LEVEL=INFO
```

### API Keys Setup

1. **RentSpider API**: Sign up at [RentSpider](https://rentspider.com/api)
2. **RealtyMole API**: Get key from [RapidAPI RealtyMole](https://rapidapi.com/realtymole/api/realtymole-rental-estimate-v1)
3. **Zillow API**: Available through [RapidAPI Zillow](https://rapidapi.com/apimaker/api/zillow-com1)
4. **Walk Score API**: Register at [Walk Score](https://www.walkscore.com/professional/api.php)

## 📚 API Usage

### Basic Examples

#### Get Properties
```bash
# Get all properties
curl "http://localhost:8000/api/v1/properties"

# Filter by city and state
curl "http://localhost:8000/api/v1/properties?city=San Francisco&state=CA"

# Filter by price range
curl "http://localhost:8000/api/v1/properties?min_price=500000&max_price=1000000"
```

#### Trigger Data Collection
```bash
# Collect data for San Francisco
curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA&sources=rentspider&sources=realtymole"
```

#### Get Market Analytics
```bash
# Get market trends for a city
curl "http://localhost:8000/api/v1/analytics/market-trends?city=San Francisco&state=CA"
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/properties` | List properties with filtering |
| GET | `/api/v1/properties/{id}` | Get property details |
| POST | `/api/v1/data/collect` | Trigger data collection |
| GET | `/api/v1/analytics/market-trends` | Get market analytics |
| GET | `/api/v1/data/sources` | List available data sources |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |

## 🗄️ Database Schema

### Core Tables

- **properties**: Main property information
- **property_history**: Price and event history
- **property_features**: Property amenities and features
- **neighborhoods**: Neighborhood statistics and scores
- **cities**: City-level market data
- **states**: State-level information
- **api_sources**: Source tracking and raw data storage

### Key Relationships

```
Properties (1) → (N) Property History
Properties (1) → (N) Property Features
Properties (N) → (1) Neighborhoods
Neighborhoods (N) → (1) Cities
Cities (N) → (1) States
```

## 🔄 Data Processing Pipeline

1. **Collection**: Fetch data from multiple APIs
2. **Normalization**: Standardize formats and data types
3. **Deduplication**: Identify and merge duplicate properties
4. **Enrichment**: Calculate derived metrics and scores
5. **Storage**: Save to PostgreSQL with proper relationships
6. **Indexing**: Optimize for query performance

## 📊 Data Quality Features

- **Address Standardization**: Consistent address formatting
- **Geocoding**: Latitude/longitude validation and correction
- **Duplicate Detection**: Fuzzy matching with confidence scores
- **Data Validation**: Type checking and range validation
- **Source Tracking**: Maintain data lineage and freshness

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=False
   export LOG_LEVEL=WARNING
   # Set secure SECRET_KEY
   ```

2. **Database Migration**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

3. **Scale Services**
   ```bash
   # Scale workers for high throughput
   docker-compose up --scale celery_worker=3
   ```

### Performance Optimization

- **Database Indexing**: Optimized indexes for common queries
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis caching for frequently accessed data
- **Background Processing**: Async tasks for data collection

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test categories
pytest tests/test_collectors.py
pytest tests/test_processors.py
pytest tests/test_api.py
```

## 📈 Monitoring and Logging

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Database and Redis connectivity monitoring
- **Metrics**: API response times and data collection statistics
- **Error Tracking**: Comprehensive error logging and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   docker-compose ps postgres
   
   # Check connection string in .env
   ```

2. **API Rate Limiting**
   ```bash
   # Check API key validity
   # Verify rate limits in collector configuration
   ```

3. **Memory Issues with Large Datasets**
   ```bash
   # Reduce batch size in configuration
   # Increase Docker memory limits
   ```

### Support

For issues and questions:
- Check the [documentation](http://localhost:8000/docs)
- Review logs: `docker-compose logs api`
- Open an issue on GitHub

## 🎯 Future Enhancements

- [ ] Machine learning price prediction models
- [ ] Real-time data streaming with WebSockets
- [ ] Advanced analytics dashboard
- [ ] Mobile API endpoints
- [ ] Multi-tenant architecture
- [ ] Advanced caching strategies
- [ ] Automated data quality monitoring