#!/bin/bash

# Real Estate Data Pipeline - Local Startup Script
echo "🏠 Starting Real Estate Data Pipeline..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it to add your API keys later."
fi

# Start the services
echo "🚀 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Access points:"
    echo "   • API: http://localhost:8000"
    echo "   • Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo ""
    echo "🧪 Test the API:"
    echo "   curl http://localhost:8000/health"
    echo ""
    echo "📊 Run demo:"
    echo "   python demo_script.py"
    echo ""
    echo "🛑 To stop:"
    echo "   docker-compose down"
else
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose logs"
fi