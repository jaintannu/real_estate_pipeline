from typing import Dict, List, Any, Optional
import logging
from .base_collector import BaseCollector
from app.config import settings

logger = logging.getLogger(__name__)


class RentCastCollector(BaseCollector):
    """
    Collector for RentCast API - provides comprehensive property data and rental estimates
    RentCast is the successor to RealtyMole API
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.rentcast_api_key,
            rate_limit=50,  # 50 requests per minute
            api_name="rentcast"  # For quota tracking
        )
        self.base_url = "https://api.rentcast.io/v1"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Return authentication headers for RentCast API
        """
        return {
            'X-Api-Key': self.api_key
        }
    
    def get_properties(self, city: str, state: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch properties for sale/rent in a given city and state
        """
        # Check quota before making request
        if not self._check_quota(1):
            logger.warning(f"Skipping RentCast request due to quota limit")
            return []
        
        try:
            url = f"{self.base_url}/listings/sale"
            params = {
                'city': city,
                'state': state,
                'limit': kwargs.get('limit', 100),
                'offset': kwargs.get('offset', 0),
                'propertyType': kwargs.get('property_type', 'all'),
                'minPrice': kwargs.get('min_price'),
                'maxPrice': kwargs.get('max_price'),
                'bedrooms': kwargs.get('bedrooms'),
                'bathrooms': kwargs.get('bathrooms'),
                'minSquareFeet': kwargs.get('min_sqft'),
                'maxSquareFeet': kwargs.get('max_sqft')
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self._make_request(url, params=params)
            
            # Record successful API usage
            self._record_quota_usage(1)
            
            # RentCast API returns a list directly, not a dictionary
            if isinstance(response, list):
                properties = response
                logger.info(f"Retrieved {len(properties)} properties from RentCast for {city}, {state}")
                return [self.normalize_property_data(prop) for prop in properties]
            elif isinstance(response, dict):
                if not self.validate_response(response):
                    return []
                properties = response.get('listings', response.get('properties', []))
                logger.info(f"Retrieved {len(properties)} properties from RentCast for {city}, {state}")
                return [self.normalize_property_data(prop) for prop in properties]
            else:
                logger.error(f"Unexpected response type from RentCast: {type(response)}")
                return []
            
        except Exception as e:
            logger.error(f"Error fetching properties from RentCast: {e}")
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
            
            property_data = response.get('property', response)
            logger.info(f"Retrieved detailed data for property {property_id} from RentCast")
            
            return self.normalize_property_data(property_data)
            
        except Exception as e:
            logger.error(f"Error fetching property details from RentCast: {e}")
            return {}
    
    def get_property_by_address(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Fetch property data by address
        """
        try:
            url = f"{self.base_url}/properties"
            params = {
                'address': address,
                'city': city,
                'state': state
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            property_data = response.get('property', response)
            logger.info(f"Retrieved property data from RentCast for {address}")
            
            return self.normalize_property_data(property_data)
            
        except Exception as e:
            logger.error(f"Error fetching property by address from RentCast: {e}")
            return {}
    
    def get_market_data(self, city: str, state: str) -> Dict[str, Any]:
        """
        Fetch market data for a given city and state
        """
        try:
            url = f"{self.base_url}/markets"
            params = {
                'city': city,
                'state': state
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            market_data = response.get('market', response)
            logger.info(f"Retrieved market data from RentCast for {city}, {state}")
            
            return self.normalize_market_data(market_data)
            
        except Exception as e:
            logger.error(f"Error fetching market data from RentCast: {e}")
            return {}
    
    def get_rental_estimate(self, address: str, city: str, state: str, 
                          bedrooms: int = None, bathrooms: int = None, 
                          square_feet: int = None) -> Dict[str, Any]:
        """
        Get rental estimate for a property using RentCast's rental estimation
        """
        try:
            url = f"{self.base_url}/avm/rent/long-term"
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
            
            rental_data = response.get('rent', response)
            logger.info(f"Retrieved rental estimate from RentCast for {address}")
            
            return {
                'estimated_rent': self._safe_float(rental_data.get('rent')),
                'rent_range_low': self._safe_float(rental_data.get('rentRangeLow')),
                'rent_range_high': self._safe_float(rental_data.get('rentRangeHigh')),
                'confidence_score': self._safe_float(rental_data.get('confidence')),
                'source': 'rentcast',
                'raw_data': rental_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching rental estimate from RentCast: {e}")
            return {}
    
    def get_property_value_estimate(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Get property value estimate using RentCast's AVM
        """
        try:
            url = f"{self.base_url}/avm/value"
            params = {
                'address': address,
                'city': city,
                'state': state
            }
            
            response = self._make_request(url, params=params)
            
            if not self.validate_response(response):
                return {}
            
            value_data = response.get('avm', response)
            logger.info(f"Retrieved value estimate from RentCast for {address}")
            
            return {
                'estimated_value': self._safe_float(value_data.get('value')),
                'value_range_low': self._safe_float(value_data.get('valueLow')),
                'value_range_high': self._safe_float(value_data.get('valueHigh')),
                'confidence_score': self._safe_float(value_data.get('confidence')),
                'source': 'rentcast',
                'raw_data': value_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching value estimate from RentCast: {e}")
            return {}
    
    def normalize_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RentCast property data to standard format
        """
        normalized = super().normalize_property_data(raw_data)
        
        # RentCast specific field mappings
        address_data = raw_data.get('address', {})
        
        normalized.update({
            'address': raw_data.get('formattedAddress', 
                      f"{address_data.get('line1', '')} {address_data.get('line2', '')}".strip()),
            'city': address_data.get('city', raw_data.get('city', '')),
            'state': address_data.get('state', raw_data.get('state', '')),
            'zip_code': address_data.get('zipCode', raw_data.get('zipCode', '')),
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
            'source': 'rentcast'
        })
        
        return normalized
    
    def normalize_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize RentCast market data
        """
        return {
            'median_price': self._safe_float(raw_data.get('medianPrice')),
            'average_price': self._safe_float(raw_data.get('averagePrice')),
            'price_change_percent': self._safe_float(raw_data.get('priceChangePercent')),
            'inventory_count': self._safe_int(raw_data.get('inventoryCount')),
            'days_on_market': self._safe_int(raw_data.get('daysOnMarket')),
            'price_per_sqft': self._safe_float(raw_data.get('pricePerSqft')),
            'sales_volume': self._safe_int(raw_data.get('salesVolume')),
            'median_rent': self._safe_float(raw_data.get('medianRent')),
            'average_rent': self._safe_float(raw_data.get('averageRent')),
            'source': 'rentcast',
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