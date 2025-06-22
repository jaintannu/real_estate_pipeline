#!/usr/bin/env python3
"""
Demo script to showcase the Real Estate Data Pipeline functionality
"""

import asyncio
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from collectors import RentSpiderCollector, RentCastCollector
from processors import DataNormalizer, DuplicateHandler, DataEnricher


async def demo_data_collection():
    """Demonstrate data collection from multiple sources"""
    logger.info("=== Real Estate Data Pipeline Demo ===")
    
    # Initialize collectors (Note: These will fail without real API keys)
    collectors = {
        'rentspider': RentSpiderCollector(),
        'rentcast': RentCastCollector()
    }
    
    # Demo city and state
    city = "San Francisco"
    state = "CA"
    
    logger.info(f"Collecting data for {city}, {state}")
    
    # Collect sample data (simulated since we don't have real API keys)
    sample_properties = [
        {
            'address': '123 Market St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94102',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'property_type': 'condo',
            'bedrooms': 2,
            'bathrooms': 2,
            'square_feet': 1200,
            'year_built': 2015,
            'current_price': 850000,
            'listing_status': 'active',
            'source': 'demo'
        },
        {
            'address': '456 Mission St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94105',
            'latitude': 37.7849,
            'longitude': -122.4094,
            'property_type': 'apartment',
            'bedrooms': 1,
            'bathrooms': 1,
            'square_feet': 800,
            'year_built': 2010,
            'current_price': 650000,
            'listing_status': 'active',
            'source': 'demo'
        },
        {
            'address': '789 Howard St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94103',
            'latitude': 37.7749,
            'longitude': -122.4094,
            'property_type': 'house',
            'bedrooms': 3,
            'bathrooms': 2,
            'square_feet': 1800,
            'year_built': 1995,
            'current_price': 1200000,
            'listing_status': 'active',
            'source': 'demo'
        },
        # Add a duplicate for testing
        {
            'address': '123 Market Street',  # Slightly different format
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94102',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'property_type': 'condominium',  # Different format
            'bedrooms': 2,
            'bathrooms': 2,
            'square_feet': 1200,
            'year_built': 2015,
            'current_price': 855000,  # Slightly different price
            'listing_status': 'active',
            'source': 'demo2'
        }
    ]
    
    logger.info(f"Collected {len(sample_properties)} sample properties")
    
    return sample_properties


def demo_data_processing(properties):
    """Demonstrate data processing pipeline"""
    logger.info("\n=== Data Processing Pipeline ===")
    
    # Initialize processors
    normalizer = DataNormalizer()
    duplicate_handler = DuplicateHandler()
    enricher = DataEnricher()
    
    # Step 1: Normalize data
    logger.info("Step 1: Normalizing data...")
    df = normalizer.normalize_properties_batch(properties)
    logger.info(f"Normalized {len(df)} properties")
    print("\nNormalized Data Sample:")
    print(df[['address', 'city', 'property_type', 'current_price']].head())
    
    # Step 2: Handle duplicates
    logger.info("\nStep 2: Detecting and handling duplicates...")
    df_with_duplicates = duplicate_handler.find_duplicates(df)
    duplicate_count = df_with_duplicates['is_duplicate'].sum() if 'is_duplicate' in df_with_duplicates.columns else 0
    logger.info(f"Found {duplicate_count} duplicate properties")
    
    df_clean = duplicate_handler.remove_duplicates(df_with_duplicates)
    logger.info(f"After deduplication: {len(df_clean)} unique properties")
    
    # Step 3: Enrich data
    logger.info("\nStep 3: Enriching data with calculated metrics...")
    df_enriched = enricher.enrich_properties(df_clean)
    logger.info(f"Enriched {len(df_enriched)} properties")
    
    # Show enriched data
    enriched_columns = ['address', 'current_price', 'price_per_sqft', 'property_age', 
                       'price_category', 'investment_score', 'family_friendly_score']
    available_columns = [col for col in enriched_columns if col in df_enriched.columns]
    
    print("\nEnriched Data Sample:")
    print(df_enriched[available_columns].head())
    
    return df_enriched


def demo_analytics(df):
    """Demonstrate analytics capabilities"""
    logger.info("\n=== Analytics Demo ===")
    
    if df.empty:
        logger.warning("No data available for analytics")
        return
    
    # Basic statistics
    logger.info("Basic Market Statistics:")
    if 'current_price' in df.columns:
        prices = df['current_price'].dropna()
        if not prices.empty:
            print(f"  Average Price: ${prices.mean():,.2f}")
            print(f"  Median Price: ${prices.median():,.2f}")
            print(f"  Price Range: ${prices.min():,.2f} - ${prices.max():,.2f}")
    
    if 'price_per_sqft' in df.columns:
        price_per_sqft = df['price_per_sqft'].dropna()
        if not price_per_sqft.empty:
            print(f"  Average Price/SqFt: ${price_per_sqft.mean():.2f}")
    
    # Property type distribution
    if 'property_type' in df.columns:
        type_counts = df['property_type'].value_counts()
        print(f"\nProperty Type Distribution:")
        for prop_type, count in type_counts.items():
            print(f"  {prop_type}: {count}")
    
    # Investment scores
    if 'investment_score' in df.columns:
        investment_scores = df['investment_score'].dropna()
        if not investment_scores.empty:
            print(f"\nInvestment Analysis:")
            print(f"  Average Investment Score: {investment_scores.mean():.2f}")
            high_investment = df[df['investment_score'] > 0.7]
            print(f"  High Investment Potential Properties: {len(high_investment)}")


def demo_api_usage():
    """Demonstrate API usage examples"""
    logger.info("\n=== API Usage Examples ===")
    
    print("Once the API is running (python -m uvicorn app.main:app --reload), you can:")
    print("\n1. Get all properties:")
    print("   curl 'http://localhost:8000/api/v1/properties'")
    
    print("\n2. Filter properties by city:")
    print("   curl 'http://localhost:8000/api/v1/properties?city=San Francisco&state=CA'")
    
    print("\n3. Trigger data collection:")
    print("   curl -X POST 'http://localhost:8000/api/v1/data/collect?city=San Francisco&state=CA'")
    
    print("\n4. Get market analytics:")
    print("   curl 'http://localhost:8000/api/v1/analytics/market-trends?city=San Francisco'")
    
    print("\n5. View API documentation:")
    print("   Open http://localhost:8000/docs in your browser")


async def main():
    """Main demo function"""
    try:
        # Demo data collection
        properties = await demo_data_collection()
        
        # Demo data processing
        processed_df = demo_data_processing(properties)
        
        # Demo analytics
        demo_analytics(processed_df)
        
        # Demo API usage
        demo_api_usage()
        
        logger.info("\n=== Demo Complete ===")
        logger.info("To run the full system:")
        logger.info("1. Set up your API keys in .env file")
        logger.info("2. Run: docker-compose up -d")
        logger.info("3. Access API at http://localhost:8000")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())