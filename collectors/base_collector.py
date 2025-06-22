from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
from utils.quota_manager import quota_manager

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    Abstract base class for all real estate data collectors
    """
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 60, api_name: str = "unknown"):
        self.api_key = api_key
        self.rate_limit = rate_limit  # requests per minute
        self.api_name = api_name  # For quota tracking
        self.last_request_time = 0
        self.session = requests.Session()
        self.base_headers = {
            'User-Agent': 'RealEstateDataPipeline/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if self.api_key:
            self.base_headers.update(self._get_auth_headers())
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Return authentication headers for the API
        """
        pass
    
    @abstractmethod
    def get_properties(self, city: str, state: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch properties for a given city and state
        """
        pass
    
    @abstractmethod
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific property
        """
        pass
    
    @abstractmethod
    def get_market_data(self, city: str, state: str) -> Dict[str, Any]:
        """
        Fetch market data for a given city and state
        """
        pass
    def _check_quota(self, num_requests: int = 1) -> bool:
        """
        Check if we can make the specified number of requests without exceeding monthly quota
        """
        if not quota_manager.can_make_request(self.api_name, num_requests):
            logger.error(f"Monthly quota exceeded for {self.api_name}. Cannot make {num_requests} request(s).")
            return False
        return True
    
    def _record_quota_usage(self, num_requests: int = 1):
        """
        Record that requests have been made for quota tracking
        """
        quota_manager.record_request(self.api_name, num_requests)
    
    def _enforce_rate_limit(self):
        """
        Enforce rate limiting between API calls
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 60.0 / self.rate_limit  # seconds between requests
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and rate limiting
        """
        self._enforce_rate_limit()
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=self.base_headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, json=data, headers=self.base_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle different content types
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                return response.json()
            else:
                return {'raw_content': response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request to {url}: {e}")
            raise
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate API response structure
        """
        if not isinstance(response, dict):
            logger.warning(f"Response is not a dictionary. Type: {type(response)}, Content: {str(response)[:500]}")
            return False
        
        if 'error' in response:
            logger.error(f"API returned error: {response['error']}")
            return False
        
        return True
    
    def normalize_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize property data to standard format
        Override in subclasses for API-specific normalization
        """
        return {
            'address': raw_data.get('address', ''),
            'city': raw_data.get('city', ''),
            'state': raw_data.get('state', ''),
            'zip_code': raw_data.get('zip_code', ''),
            'latitude': raw_data.get('latitude'),
            'longitude': raw_data.get('longitude'),
            'property_type': raw_data.get('property_type', ''),
            'bedrooms': raw_data.get('bedrooms'),
            'bathrooms': raw_data.get('bathrooms'),
            'square_feet': raw_data.get('square_feet'),
            'lot_size': raw_data.get('lot_size'),
            'year_built': raw_data.get('year_built'),
            'current_price': raw_data.get('price'),
            'listing_status': raw_data.get('status', ''),
            'raw_data': raw_data  # Store original data for reference
        }
    
    def get_collector_name(self) -> str:
        """
        Return the name of this collector
        """
        return self.__class__.__name__.replace('Collector', '').lower()