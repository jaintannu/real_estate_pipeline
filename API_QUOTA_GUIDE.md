# API Quota Management System

## Overview
The real estate data pipeline now includes a comprehensive quota management system to ensure you never exceed your monthly API limits. This system enforces strict limits of **50 requests/month for RentCast** and **100 requests/month for Zillow**.

## Monthly Limits
- **RentCast API**: 50 requests/month
- **Zillow API**: 100 requests/month  
- **RentSpider API**: 1000 requests/month (higher limit)
- **Demo Collector**: Unlimited (no real API calls)

## How It Works

### 1. Automatic Quota Tracking
- Every API request is tracked and recorded
- Quotas reset automatically on the 1st of each month
- Persistent storage in `api_quotas.json` file

### 2. Pre-Request Validation
- Before making any API call, the system checks remaining quota
- If quota is exceeded, the request is blocked and logged
- No API calls are made if quota limit is reached

### 3. Real-Time Monitoring
- Track usage in real-time via API endpoints
- Get detailed status for each API service
- Monitor remaining requests and reset dates

## API Endpoints

### Check All Quota Status
```bash
GET /api/v1/quota/status
```

**Response:**
```json
{
  "status": "success",
  "quota_status": {
    "rentcast": {
      "api_name": "rentcast",
      "used": 5,
      "limit": 50,
      "remaining": 45,
      "reset_date": "2025-07-01T00:00:00",
      "days_until_reset": 11
    },
    "zillow": {
      "api_name": "zillow", 
      "used": 0,
      "limit": 100,
      "remaining": 100,
      "reset_date": "2025-07-01T00:00:00",
      "days_until_reset": 11
    }
  },
  "timestamp": "2025-06-20T16:05:27"
}
```

### Check Specific API Quota
```bash
GET /api/v1/quota/status/rentcast
```

## Data Collection with Quota Protection

### Safe Data Collection
```bash
# This will automatically check quota before making requests
POST /api/v1/data/collect?city=San Francisco&state=CA&sources=rentcast
```

### Demo Mode (No Quota Usage)
```bash
# Use demo collector for testing without using quota
POST /api/v1/data/collect?city=San Francisco&state=CA&sources=demo
```

## Quota Protection Features

### 1. Automatic Blocking
- Requests are blocked when quota is exceeded
- Clear error messages explain quota status
- No accidental API calls beyond limits

### 2. Graceful Degradation
- System continues working with available APIs
- Demo data available when quotas are exhausted
- Detailed logging of quota decisions

### 3. Monthly Reset
- Quotas automatically reset on the 1st of each month
- No manual intervention required
- Persistent tracking across application restarts

## Configuration

### Environment Variables
```bash
# Add your API keys to .env file
RENTCAST_API_KEY=your_rentcast_api_key_here
ZILLOW_API_KEY=your_zillow_api_key_here
```

### Quota Limits
Limits are configured in [`utils/quota_manager.py`](utils/quota_manager.py:25):
```python
self.monthly_limits = {
    'rentcast': 50,      # Your requirement
    'zillow': 100,       # Your requirement  
    'rentspider': 1000,  # Higher limit
    'demo': float('inf') # No limit
}
```

## Usage Examples

### 1. Check Current Status
```bash
curl "http://localhost:8000/api/v1/quota/status"
```

### 2. Collect Data Safely
```bash
# Will respect quota limits automatically
curl -X POST "http://localhost:8000/api/v1/data/collect?city=Los Angeles&state=CA&sources=rentcast"
```

### 3. Use Demo Mode for Testing
```bash
# No quota usage - perfect for development
curl -X POST "http://localhost:8000/api/v1/data/collect?city=Los Angeles&state=CA&sources=demo"
```

## Monitoring and Alerts

### Log Messages
The system provides detailed logging:
- `INFO`: Successful quota checks and API usage recording
- `WARNING`: Quota approaching limits or requests blocked
- `ERROR`: Quota exceeded attempts

### Example Log Output
```
2025-06-20 16:05:27 - utils.quota_manager - INFO - Recorded 1 request(s) for rentcast. Used: 6/50
2025-06-20 16:05:28 - utils.quota_manager - WARNING - Quota exceeded for rentcast. Used: 50/50, Requested: 1, Remaining: 0
2025-06-20 16:05:29 - collectors.rentcast_collector - WARNING - Skipping RentCast request due to quota limit
```

## Best Practices

### 1. Monitor Usage Regularly
- Check quota status before large data collection operations
- Use the `/api/v1/quota/status` endpoint to track usage

### 2. Use Demo Mode for Development
- Test your application logic with demo data
- Save real API calls for production data collection

### 3. Plan Data Collection
- Spread API calls throughout the month
- Prioritize most important data sources
- Use multiple APIs to maximize data collection

### 4. Handle Quota Exhaustion
- Implement fallback to demo data when quotas are exceeded
- Queue requests for next month if needed
- Monitor reset dates for planning

## Troubleshooting

### Quota File Issues
If you encounter quota tracking issues:
```bash
# Remove quota file to reset (use carefully!)
rm api_quotas.json

# Restart the application
docker-compose restart api
```

### Manual Quota Reset (Admin Only)
```python
from utils.quota_manager import quota_manager

# Reset specific API quota
quota_manager.reset_quota('rentcast')

# Set custom limits
quota_manager.set_monthly_limit('rentcast', 75)
```

## Security Notes
- Quota data is stored locally in `api_quotas.json`
- File contains usage statistics but no sensitive data
- Backup quota file if you need to preserve usage history

## Integration with Existing Code
The quota system is fully integrated and requires no changes to existing API calls. All collectors automatically:
1. Check quota before making requests
2. Record successful API usage
3. Block requests when limits are exceeded
4. Provide clear feedback on quota status

This ensures you'll never accidentally exceed your 50 requests/month for RentCast or 100 requests/month for Zillow!