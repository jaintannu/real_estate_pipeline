# RentCast API Setup Guide

## Overview
RentCast API has replaced RealtyMole as the primary real estate data source. RentCast provides comprehensive property data, rental estimates, and market analytics.

## API Key Setup

### 1. Get Your RentCast API Key
- Visit [RentCast.io](https://rentcast.io)
- Sign up for an account
- Navigate to your dashboard to get your API key

### 2. Add API Key to Environment
Edit your `.env` file and add your RentCast API key:
```
RENTCAST_API_KEY=your_actual_rentcast_api_key_here
```

## Using the RentCast Collector

### Available Data Sources
- `rentspider` - RentSpider API (existing)
- `rentcast` - RentCast API (new, replaces realtymole)
- `demo` - Demo data generator (for testing)

### API Endpoints

#### Collect Data with RentCast
```bash
POST /api/v1/data/collect?city=San Francisco&state=CA&sources=rentcast
```

#### Collect Data with Multiple Sources
```bash
POST /api/v1/data/collect?city=San Francisco&state=CA&sources=rentspider,rentcast
```

#### Demo Data (No API Key Required)
```bash
POST /api/v1/data/collect?city=San Francisco&state=CA&sources=demo
```

## RentCast Features

### Property Data
- Property listings for sale and rent
- Detailed property information
- Address-based property lookup
- Property value estimates (AVM)
- Rental estimates

### Market Data
- Market trends and analytics
- Median prices and rent data
- Inventory counts
- Days on market statistics

### Rate Limits
- 50 requests per minute
- Automatic rate limiting built-in

## Example Usage

### 1. Test with Demo Data (No API Key)
```bash
curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA&sources=demo"
```

### 2. Use RentCast API (Requires API Key)
```bash
curl -X POST "http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA&sources=rentcast"
```

### 3. View Collected Properties
```bash
curl "http://localhost:8000/api/v1/properties"
```

## Migration from RealtyMole

### What Changed
- `realtymole` source replaced with `rentcast`
- Updated API endpoints and data structure
- Enhanced property and market data features
- Improved rate limiting and error handling

### Configuration Updates
- Replace `REALTYMOLE_API_KEY` with `RENTCAST_API_KEY` in `.env`
- Update API calls from `sources=realtymole` to `sources=rentcast`
- No database schema changes required

## Troubleshooting

### Common Issues
1. **Invalid API Key**: Ensure your RentCast API key is correctly set in `.env`
2. **Rate Limiting**: RentCast has a 50 requests/minute limit
3. **No Data Returned**: Check city/state spelling and API key validity

### Support
- RentCast API Documentation: [docs.rentcast.io](https://docs.rentcast.io)
- RentCast Support: support@rentcast.io

## Next Steps
1. Sign up for RentCast API
2. Add your API key to `.env` file
3. Test the data collection endpoint
4. Integrate with your real estate application