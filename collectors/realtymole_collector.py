from typing import Dict, List, Any, Optional
import logging
from .base_collector import BaseCollector
from app.config import settings

logger = logging.getLogger(__name__)


class RealtyMoleCollector(BaseCollector):
    """
    Collector for RealtyMole API - provides comprehensive property data and comparables
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.realtymole_api_key,
            rate_limit=50  # 50 requests per minute
        )
        self.base_url = "https://api.realtymole.com/v1"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Return authentication headers for RealtyMole API
        """
        return {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'realtymole-rental-estimate-v1.p.rapidapi.com'
        }
    
    def get_properties(self, city: str, state: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch properties for sale/rent in a given city and state
        """
        try:
            url = f"{self.base_url}/properties"
            params = {
                'city': city,
                'state': state,
                'limit': kwargs.get('limit', 100),
                'offset': kwargs.get('offset', 0),
                'propertyType': kwargs.get('property_type', 'all'),
                'minPrice': kwargs.get('min_price'),
                'maxPrice': kwargs.get('max_price'),
                'beds': kwargs.get('bedrooms'),
                'baths': kwargs.get('bathrooms'),
                'minSqft': kwargs.get('min_sqft'),
                'maxSqft': kwargs.get('max_sqft')
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return []
            
            properties = response.get('listings', response.get('properties', []))
            logger.info(f"Retrieved {len(properties)} properties from RealtyMole for {city}, {state}")
            
            return [self.normalize_property_data(prop) for prop in properties]
            
        except Exception as e:
            logger.error(f"Error fetching properties from RealtyMole: {e}")
            return []
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific property
        """
        try:
            url = f"{self.base_url}/property/{property_id}"
            response = self._make_request(url)
            
            if not self.validate_response(response):
                return {}
            
            property_data = response.get('property', response)
            logger.info(f"Retrieved detailed data for property {property_id} from RealtyMole")
            
            return self.normalize_property_data(property_data)
            
        except Exception as e:
            logger.error(f"Error fetching property details from RealtyMole: {e}")
            return {}
    
    def get_property_comparables(self, address: str, city: str, state: str) -> List[Dict[str, Any]]:
        """
        Fetch comparable properties for a given address
        """
        try:
            url = f"{self.base_url}/comparables"
            params = {
                'address': address,
                'city': city,
                'state': state,
                'limit': 10
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return []
            
            comparables = response.get('comparables', [])
            logger.info(f"Retrieved {len(comparables)} comparables from RealtyMole for {address}")
            
            return [self.normalize_property_data(comp) for comp in comparables]
            
        except Exception as e:
            logger.error(f"Error fetching comparables from RealtyMole: {e}")
            return []
    
    def get_market_data(self, city: str, state: str) -> Dict[str, Any]:
        """
        Fetch market data for a given city and state
        """
        try:
            url = f"{self.base_url}/market-data"
            params = {
                'city': city,
                'state': state
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            market_data = response.get('marketData', response)
            logger.info(f"Retrieved market data from RealtyMole for {city}, {state}")
            
            return self.normalize_market_data(market_data)
            
        except Exception as e:
            logger.error(f"Error fetching market data from RealtyMole: {e}")
            return {}
    
    def get_rental_estimate(self, address: str, city: str, state: str, 
                          bedrooms: int = None, bathrooms: int = None, 
                          square_feet: int = None) -> Dict[str, Any]:
        """
        Get rental estimate for a property
        """
        try:
            url = f"{self.base_url}/rentalPrice"
            params = {
                'address': address,
                'city': city,
                'state': state
            }
            
            if bedrooms:
                params['bedrooms'] = bedrooms
            if bathrooms:
                params['bathrooms'] = bathrooms
            if square_feet:
                params['squareFootage'] = square_feet
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            rental_data = response.get('rentalData', response)
            logger.info(f"Retrieved rental estimate from RealtyMole for {address}")
            
            return {
                'estimated_rent': self._safe_float(rental_data.get('rent')),
                'rent_range_low': self._safe_float(rental_data.get('rentRangeLow')),
                'rent_range_high': self._safe_float(rental_data.get('rentRangeHigh')),
                'confidence_score': self._safe_float(rental_data.get('confidence')),
                'source': 'realtymole',
                'raw_data': rental_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching rental estimate from RealtyMole: {e}")
            return {}
    
    def normalize_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RealtyMole property data to standard format
        """
        normalized = super().normalize_property_data(raw_data)
        
        # RealtyMole specific field mappings
        address_data = raw_data.get('address', {})
        
        normalized.update({
            'address': raw_data.get('formattedAddress', 
                      f"{address_data.get('line', '')} {address_data.get('line2', '')}".strip()),
            'city': address_data.get('city', raw_data.get('city', '')),
            'state': address_data.get('state', raw_data.get('state', '')),
            'zip_code': address_data.get('zip', raw_data.get('zipCode', '')),
            'latitude': self._safe_float(raw_data.get('latitude', raw_data.get('lat'))),
            'longitude': self._safe_float(raw_data.get('longitude', raw_data.get('lng'))),
            'property_type': raw_data.get('propertyType', raw_data.get('type', '')),
            'bedrooms': self._safe_int(raw_data.get('bedrooms', raw_data.get('beds'))),
            'bathrooms': self._safe_int(raw_data.get('bathrooms', raw_data.get('baths'))),
            'square_feet': self._safe_int(raw_data.get('squareFootage', raw_data.get('sqft'))),
            'lot_size': self._safe_float(raw_data.get('lotSize')),
            'year_built': self._safe_int(raw_data.get('yearBuilt')),
            'current_price': self._safe_float(raw_data.get('price', raw_data.get('listPrice'))),
            'listing_status': raw_data.get('status', raw_data.get('listingStatus', '')),
            'source': 'realtymole'
        })
        
        return normalized
    
    def normalize_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RealtyMole market data
        """
        return {
            'median_price': self._safe_float(raw_data.get('medianPrice')),
            'average_price': self._safe_float(raw_data.get('averagePrice')),
            'price_change_percent': self._safe_float(raw_data.get('priceChangePercent')),
            'inventory_count': self._safe_int(raw_data.get('inventoryCount')),
            'days_on_market': self._safe_int(raw_data.get('daysOnMarket')),
            'price_per_sqft': self._safe_float(raw_data.get('pricePerSqft')),
            'sales_volume': self._safe_int(raw_data.get('salesVolume')),
            'source': 'realtymole',
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