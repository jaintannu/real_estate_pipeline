from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.config import settings
from app.database import get_db, create_tables
from models import Property, PropertyHistory, Neighborhood, City, State, MarketTrend
from collectors import RentSpiderCollector, RentCastCollector, DemoCollector
from processors import DataNormalizer, DuplicateHandler, DataEnricher
from utils.quota_manager import quota_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Real Estate Data Pipeline API",
    description="API for collecting, processing, and serving real estate data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
data_normalizer = DataNormalizer()
duplicate_handler = DuplicateHandler()
data_enricher = DataEnricher()

# Initialize collectors
collectors = {
    'rentspider': RentSpiderCollector(),
    'rentcast': RentCastCollector(),
    'demo': DemoCollector()
}


@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    try:
        create_tables()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Real Estate Data Pipeline API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Property endpoints
@app.get("/api/v1/properties", response_model=List[Dict[str, Any]])
async def get_properties(
    db: Session = Depends(get_db),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    bedrooms: Optional[int] = Query(None, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, description="Number of bathrooms"),
    property_type: Optional[str] = Query(None, description="Property type"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get properties with optional filtering"""
    try:
        query = db.query(Property)
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Property.state.ilike(f"%{state}%"))
        if min_price:
            query = query.filter(Property.current_price >= min_price)
        if max_price:
            query = query.filter(Property.current_price <= max_price)
        if bedrooms:
            query = query.filter(Property.bedrooms == bedrooms)
        if bathrooms:
            query = query.filter(Property.bathrooms == bathrooms)
        if property_type:
            query = query.filter(Property.property_type.ilike(f"%{property_type}%"))
        
        # Apply pagination
        properties = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        result = []
        for prop in properties:
            # Helper function to safely convert to float and handle NaN
            def safe_float(value):
                if value is None:
                    return None
                try:
                    float_val = float(value)
                    # Check for NaN or infinity
                    if not (float_val == float_val) or float_val in [float('inf'), float('-inf')]:
                        return None
                    return float_val
                except (ValueError, TypeError):
                    return None
            
            prop_dict = {
                'id': str(prop.id),
                'address': prop.address,
                'city': prop.city,
                'state': prop.state,
                'zip_code': prop.zip_code,
                'latitude': safe_float(prop.latitude),
                'longitude': safe_float(prop.longitude),
                'property_type': prop.property_type,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'square_feet': prop.square_feet,
                'lot_size': safe_float(prop.lot_size),
                'year_built': prop.year_built,
                'current_price': safe_float(prop.current_price),
                'listing_status': prop.listing_status,
                'created_at': prop.created_at.isoformat() if prop.created_at else None,
                'updated_at': prop.updated_at.isoformat() if prop.updated_at else None
            }
            result.append(prop_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/properties/{property_id}")
async def get_property_details(
    property_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific property"""
    try:
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Helper function to safely convert to float and handle NaN
        def safe_float(value):
            if value is None:
                return None
            try:
                float_val = float(value)
                # Check for NaN or infinity
                if not (float_val == float_val) or float_val in [float('inf'), float('-inf')]:
                    return None
                return float_val
            except (ValueError, TypeError):
                return None
        
        # Get related data
        history = db.query(PropertyHistory).filter(PropertyHistory.property_id == property_id).all()
        
        result = {
            'id': str(property_obj.id),
            'address': property_obj.address,
            'city': property_obj.city,
            'state': property_obj.state,
            'zip_code': property_obj.zip_code,
            'latitude': safe_float(property_obj.latitude),
            'longitude': safe_float(property_obj.longitude),
            'property_type': property_obj.property_type,
            'bedrooms': property_obj.bedrooms,
            'bathrooms': property_obj.bathrooms,
            'square_feet': property_obj.square_feet,
            'lot_size': safe_float(property_obj.lot_size),
            'year_built': property_obj.year_built,
            'current_price': safe_float(property_obj.current_price),
            'listing_status': property_obj.listing_status,
            'created_at': property_obj.created_at.isoformat() if property_obj.created_at else None,
            'updated_at': property_obj.updated_at.isoformat() if property_obj.updated_at else None,
            'price_history': [
                {
                    'price': safe_float(h.price),
                    'event_type': h.event_type,
                    'event_date': h.event_date.isoformat(),
                    'source': h.source
                } for h in history
            ]
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching property details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/data/collect")
async def trigger_data_collection(
    background_tasks: BackgroundTasks,
    city: str = Query(..., description="City to collect data for"),
    state: str = Query(..., description="State to collect data for"),
    sources: List[str] = Query(['rentspider', 'rentcast'], description="Data sources to use"),
    db: Session = Depends(get_db)
):
    """Trigger data collection for a specific city and state"""
    try:
        # Validate sources
        invalid_sources = [s for s in sources if s not in collectors.keys()]
        if invalid_sources:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid sources: {invalid_sources}. Available: {list(collectors.keys())}"
            )
        
        # Add background task
        background_tasks.add_task(
            collect_and_process_data,
            city=city,
            state=state,
            sources=sources,
            db=db
        )
        
        return {
            "message": f"Data collection started for {city}, {state}",
            "sources": sources,
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering data collection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def collect_and_process_data(city: str, state: str, sources: List[str], db: Session):
    """Background task to collect and process data"""
    
    def safe_value(value):
        """
        Safely convert values to prevent NaN from being inserted into database
        """
        if value is None:
            return None
        
        # Handle pandas NaN values
        try:
            import pandas as pd
            if pd.isna(value):
                return None
        except (ImportError, TypeError):
            pass
        
        # Handle Python float NaN values
        try:
            if isinstance(value, float):
                if not (value == value):  # NaN check
                    return None
                if value in [float('inf'), float('-inf')]:
                    return None
        except (TypeError, ValueError):
            pass
        
        return value
    
    try:
        logger.info(f"Starting data collection for {city}, {state} from sources: {sources}")
        
        all_properties = []
        
        # Collect data from each source
        for source_name in sources:
            if source_name in collectors:
                collector = collectors[source_name]
                try:
                    properties = collector.get_properties(city, state, limit=100)
                    all_properties.extend(properties)
                    logger.info(f"Collected {len(properties)} properties from {source_name}")
                except Exception as e:
                    logger.error(f"Error collecting from {source_name}: {e}")
        
        if not all_properties:
            logger.warning(f"No properties collected for {city}, {state}")
            return
        
        # Process the data
        logger.info(f"Processing {len(all_properties)} properties")
        
        # Normalize data
        df = data_normalizer.normalize_properties_batch(all_properties)
        if df.empty:
            logger.warning("No properties after normalization")
            return
        
        # Handle duplicates
        df = duplicate_handler.remove_duplicates(df)
        
        # Enrich data
        df = data_enricher.enrich_properties(df)
        
        # Save to database
        saved_count = 0
        for _, row in df.iterrows():
            try:
                # Check if property already exists
                existing = db.query(Property).filter(
                    Property.address == row.get('address'),
                    Property.city == row.get('city'),
                    Property.state == row.get('state')
                ).first()
                
                if existing:
                    # Update existing property with safe value conversion
                    for key, value in row.items():
                        safe_val = safe_value(value)
                        if hasattr(existing, key) and safe_val is not None:
                            setattr(existing, key, safe_val)
                else:
                    # Create new property with safe value conversion
                    property_data = {
                        'address': safe_value(row.get('address')),
                        'city': safe_value(row.get('city')),
                        'state': safe_value(row.get('state')),
                        'zip_code': safe_value(row.get('zip_code')),
                        'latitude': safe_value(row.get('latitude')),
                        'longitude': safe_value(row.get('longitude')),
                        'property_type': safe_value(row.get('property_type')),
                        'bedrooms': safe_value(row.get('bedrooms')),
                        'bathrooms': safe_value(row.get('bathrooms')),
                        'square_feet': safe_value(row.get('square_feet')),
                        'lot_size': safe_value(row.get('lot_size')),
                        'year_built': safe_value(row.get('year_built')),
                        'current_price': safe_value(row.get('current_price')),
                        'listing_status': safe_value(row.get('listing_status', 'active'))
                    }
                    
                    # Remove None values (now safe from NaN contamination)
                    property_data = {k: v for k, v in property_data.items() if v is not None}
                    
                    new_property = Property(**property_data)
                    db.add(new_property)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving property: {e}")
                continue
        
        # Commit changes
        db.commit()
        logger.info(f"Successfully saved/updated {saved_count} properties for {city}, {state}")
        
    except Exception as e:
        logger.error(f"Error in background data collection task: {e}")
        db.rollback()


@app.get("/api/v1/analytics/market-trends")
async def get_market_trends(
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db)
):
    """Get market trend analytics"""
    try:
        query = db.query(Property)
        
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Property.state.ilike(f"%{state}%"))
        
        properties = query.all()
        
        if not properties:
            return {"message": "No data available for the specified filters"}
        
        # Calculate basic statistics
        prices = [float(p.current_price) for p in properties if p.current_price]
        sqft_values = [p.square_feet for p in properties if p.square_feet]
        
        if not prices:
            return {"message": "No price data available"}
        
        result = {
            "total_properties": len(properties),
            "price_statistics": {
                "median_price": sorted(prices)[len(prices)//2] if prices else None,
                "average_price": sum(prices) / len(prices) if prices else None,
                "min_price": min(prices) if prices else None,
                "max_price": max(prices) if prices else None
            },
            "size_statistics": {
                "median_sqft": sorted(sqft_values)[len(sqft_values)//2] if sqft_values else None,
                "average_sqft": sum(sqft_values) / len(sqft_values) if sqft_values else None
            },
            "property_types": {},
            "filters_applied": {
                "city": city,
                "state": state
            }
        }
        
        # Property type distribution
        type_counts = {}
        for prop in properties:
            prop_type = prop.property_type or 'unknown'
            type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
        
        result["property_types"] = type_counts
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/data/sources")
async def get_data_sources():
    """Get available data sources"""
    return {
        "available_sources": list(collectors.keys()),
        "source_details": {
            name: {
                "name": collector.get_collector_name(),
                "rate_limit": collector.rate_limit
            }
            for name, collector in collectors.items()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
# API Quota Management Endpoints
@app.get("/api/v1/quota/status")
async def get_quota_status():
    """
    Get current API quota status for all services
    """
    try:
        status = quota_manager.get_all_quota_status()
        return {
            "status": "success",
            "quota_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting quota status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting quota status: {str(e)}")

@app.get("/api/v1/quota/status/{api_name}")
async def get_api_quota_status(api_name: str):
    """
    Get quota status for a specific API
    """
    try:
        if api_name not in ['rentcast', 'zillow', 'rentspider', 'demo']:
            raise HTTPException(status_code=400, detail=f"Unknown API: {api_name}")
        
        status = quota_manager.get_quota_status(api_name)
        return {
            "status": "success",
            "quota_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quota status for {api_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting quota status: {str(e)}")