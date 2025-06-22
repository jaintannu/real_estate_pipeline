from typing import Dict, List, Any
import logging
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class DemoCollector(BaseCollector):
    """
    Demo collector that provides sample data without needing API keys
    """
    
    def __init__(self):
        super().__init__(api_key=None, rate_limit=10)
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        No authentication needed for demo
        """
        return {}
    
    def get_properties(self, city: str, state: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return sample properties for demo purposes
        """
        try:
            logger.info(f"Demo collector: Generating sample data for {city}, {state}")
            
            # Sample property data
            sample_properties = [
                {
                    'address': '123 Market St',
                    'city': city,
                    'state': state,
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
                    'city': city,
                    'state': state,
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
                    'city': city,
                    'state': state,
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
                }
            ]
            
            logger.info(f"Demo collector: Generated {len(sample_properties)} sample properties")
            return sample_properties
            
        except Exception as e:
            logger.error(f"Error in demo collector: {e}")
            return []
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Return sample property details
        """
        return {
            'address': '123 Sample St',
            'city': 'Demo City',
            'state': 'CA',
            'bedrooms': 2,
            'bathrooms': 2,
            'square_feet': 1200,
            'current_price': 750000,
            'source': 'demo'
        }
    
    def get_market_data(self, city: str, state: str) -> Dict[str, Any]:
        """
        Return sample market data
        """
        return {
            'median_price': 800000,
            'average_price': 850000,
            'inventory_count': 150,
            'days_on_market': 25,
            'source': 'demo'
        }