from typing import Dict, List, Any, Optional
import logging
from .base_collector import BaseCollector
from app.config import settings

logger = logging.getLogger(__name__)


class RentSpiderCollector(BaseCollector):
    """
    Collector for RentSpider API - provides rental property data
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.rentspider_api_key,
            rate_limit=60  # 60 requests per minute
        )
        self.base_url = "https://api.rentspider.com/v1"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Return authentication headers for RentSpider API
        """
        return {
            'X-API-Key': self.api_key
        }
    
    def get_properties(self, city: str, state: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch rental properties for a given city and state
        """
        try:
            url = f"{self.base_url}/properties/search"
            params = {
                'city': city,
                'state': state,
                'limit': kwargs.get('limit', 100),
                'offset': kwargs.get('offset', 0),
                'property_type': kwargs.get('property_type', 'all'),
                'min_price': kwargs.get('min_price'),
                'max_price': kwargs.get('max_price'),
                'bedrooms': kwargs.get('bedrooms'),
                'bathrooms': kwargs.get('bathrooms')
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return []
            
            properties = response.get('properties', [])
            logger.info(f"Retrieved {len(properties)} properties from RentSpider for {city}, {state}")
            
            return [self.normalize_property_data(prop) for prop in properties]
            
        except Exception as e:
            logger.error(f"Error fetching properties from RentSpider: {e}")
            return []
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific property
        """
        try:
            url = f"{self.base_url}/properties/{property_id}"
            response = self._make_request(url)
            
            if not self.validate_response(response):
                return {}
            
            property_data = response.get('property', {})
            logger.info(f"Retrieved detailed data for property {property_id} from RentSpider")
            
            return self.normalize_property_data(property_data)
            
        except Exception as e:
            logger.error(f"Error fetching property details from RentSpider: {e}")
            return {}
    
    def get_market_data(self, city: str, state: str) -> Dict[str, Any]:
        """
        Fetch rental market data for a given city and state
        """
        try:
            url = f"{self.base_url}/market/stats"
            params = {
                'city': city,
                'state': state,
                'period': 'monthly'
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            market_data = response.get('market_stats', {})
            logger.info(f"Retrieved market data from RentSpider for {city}, {state}")
            
            return self.normalize_market_data(market_data)
            
        except Exception as e:
            logger.error(f"Error fetching market data from RentSpider: {e}")
            return {}
    
    def normalize_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RentSpider property data to standard format
        """
        normalized = super().normalize_property_data(raw_data)
        
        # RentSpider specific field mappings
        normalized.update({
            'address': raw_data.get('full_address', raw_data.get('address', '')),
            'city': raw_data.get('city', ''),
            'state': raw_data.get('state_code', raw_data.get('state', '')),
            'zip_code': raw_data.get('postal_code', raw_data.get('zip_code', '')),
            'latitude': self._safe_float(raw_data.get('lat', raw_data.get('latitude'))),
            'longitude': self._safe_float(raw_data.get('lng', raw_data.get('longitude'))),
            'property_type': raw_data.get('type', raw_data.get('property_type', '')),
            'bedrooms': self._safe_int(raw_data.get('beds', raw_data.get('bedrooms'))),
            'bathrooms': self._safe_int(raw_data.get('baths', raw_data.get('bathrooms'))),
            'square_feet': self._safe_int(raw_data.get('sqft', raw_data.get('square_feet'))),
            'current_price': self._safe_float(raw_data.get('rent', raw_data.get('price'))),
            'listing_status': raw_data.get('availability', raw_data.get('status', 'available')),
            'source': 'rentspider'
        })
        
        return normalized
    
    def normalize_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RentSpider market data
        """
        return {
            'median_rent': self._safe_float(raw_data.get('median_rent')),
            'average_rent': self._safe_float(raw_data.get('average_rent')),
            'rent_change_percent': self._safe_float(raw_data.get('rent_change_percent')),
            'inventory_count': self._safe_int(raw_data.get('total_listings')),
            'days_on_market': self._safe_int(raw_data.get('avg_days_on_market')),
            'occupancy_rate': self._safe_float(raw_data.get('occupancy_rate')),
            'source': 'rentspider',
            'raw_data': raw_data
        }
    
    def _safe_int(self, value) -> Optional[int]:
        """
        Safely convert value to integer
        """
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value) -> Optional[float]:
        """
        Safely convert value to float
        """
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None