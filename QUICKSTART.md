# 🚀 Quick Start Guide

## Run the Project in 3 Steps

### Step 1: Prerequisites
Make sure you have **Docker Desktop** installed and running:
- Download from: https://www.docker.com/products/docker-desktop/

### Step 2: Start the Project
```bash
cd real_estate_pipeline
./start_local.sh
```

### Step 3: Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000

## 🧪 Test It Works

### Option 1: Use the Web Interface
1. Open http://localhost:8000/docs
2. Try the `/health` endpoint
3. Try the `/api/v1/properties` endpoint

### Option 2: Use Command Line
```bash
# Health check
curl http://localhost:8000/health

# Get properties (will be empty initially)
curl http://localhost:8000/api/v1/properties

# Trigger demo data collection
curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA"
```

### Option 3: Run Demo Script
```bash
python demo_script.py
```

## 🛑 Stop the Project
```bash
docker-compose down
```

## 🔧 Troubleshooting

**If Docker isn't running:**
- Start Docker Desktop application
- Wait for it to fully start (green icon)

**If ports are busy:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

**If services fail to start:**
```bash
# Check logs
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

## 📚 What's Next?

1. **Add Real API Keys**: Edit `.env` file with actual API keys
2. **Explore API**: Use http://localhost:8000/docs
3. **Read Full Documentation**: See `README.md` and `LOCAL_SETUP.md`
4. **Customize**: Add your own data sources in `collectors/`

---

**That's it! Your real estate data pipeline is running! 🎉**