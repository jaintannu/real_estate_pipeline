import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QuotaManager:
    """
    Manages API quota limits to prevent exceeding monthly limits
    """
    
    def __init__(self, quota_file: str = "api_quotas.json"):
        self.quota_file = quota_file
        self.quotas = self._load_quotas()
        
        # Default monthly limits
        self.monthly_limits = {
            'rentcast': 50,
            'zillow': 100,
            'rentspider': 1000,  # Assuming higher limit
            'demo': float('inf')  # No limit for demo
        }
    
    def _load_quotas(self) -> Dict:
        """Load quota data from file"""
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                    # Convert string dates back to datetime objects
                    for api_name in data:
                        if 'reset_date' in data[api_name]:
                            data[api_name]['reset_date'] = datetime.fromisoformat(
                                data[api_name]['reset_date']
                            )
                    return data
            except Exception as e:
                logger.error(f"Error loading quota file: {e}")
                return {}
        return {}
    
    def _save_quotas(self):
        """Save quota data to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = {}
            for api_name, quota_info in self.quotas.items():
                data_to_save[api_name] = quota_info.copy()
                if 'reset_date' in quota_info:
                    data_to_save[api_name]['reset_date'] = quota_info['reset_date'].isoformat()
            
            with open(self.quota_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving quota file: {e}")
    
    def _get_current_month_start(self) -> datetime:
        """Get the start of the current month"""
        now = datetime.now()
        return datetime(now.year, now.month, 1)
    
    def _initialize_api_quota(self, api_name: str):
        """Initialize quota tracking for an API"""
        if api_name not in self.quotas:
            self.quotas[api_name] = {
                'used': 0,
                'reset_date': self._get_next_month_start(),
                'limit': self.monthly_limits.get(api_name, 1000)
            }
    
    def _get_next_month_start(self) -> datetime:
        """Get the start of the next month"""
        now = datetime.now()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)
    
    def _reset_quota_if_needed(self, api_name: str):
        """Reset quota if we've passed the reset date"""
        if api_name in self.quotas:
            if datetime.now() >= self.quotas[api_name]['reset_date']:
                self.quotas[api_name]['used'] = 0
                self.quotas[api_name]['reset_date'] = self._get_next_month_start()
                logger.info(f"Reset monthly quota for {api_name}")
    
    def can_make_request(self, api_name: str, num_requests: int = 1) -> bool:
        """
        Check if we can make the specified number of requests without exceeding quota
        """
        self._initialize_api_quota(api_name)
        self._reset_quota_if_needed(api_name)
        
        quota_info = self.quotas[api_name]
        remaining = quota_info['limit'] - quota_info['used']
        
        can_make = remaining >= num_requests
        
        if not can_make:
            logger.warning(
                f"Quota exceeded for {api_name}. "
                f"Used: {quota_info['used']}/{quota_info['limit']}, "
                f"Requested: {num_requests}, "
                f"Remaining: {remaining}"
            )
        
        return can_make
    
    def record_request(self, api_name: str, num_requests: int = 1):
        """Record that requests have been made"""
        self._initialize_api_quota(api_name)
        self._reset_quota_if_needed(api_name)
        
        self.quotas[api_name]['used'] += num_requests
        self._save_quotas()
        
        logger.info(
            f"Recorded {num_requests} request(s) for {api_name}. "
            f"Used: {self.quotas[api_name]['used']}/{self.quotas[api_name]['limit']}"
        )
    
    def get_quota_status(self, api_name: str) -> Dict:
        """Get current quota status for an API"""
        self._initialize_api_quota(api_name)
        self._reset_quota_if_needed(api_name)
        
        quota_info = self.quotas[api_name]
        
        # Handle infinite limits for JSON serialization
        limit = quota_info['limit']
        if limit == float('inf'):
            limit_display = "unlimited"
            remaining_display = "unlimited"
        else:
            limit_display = limit
            remaining_display = limit - quota_info['used']
        
        return {
            'api_name': api_name,
            'used': quota_info['used'],
            'limit': limit_display,
            'remaining': remaining_display,
            'reset_date': quota_info['reset_date'].isoformat(),
            'days_until_reset': (quota_info['reset_date'] - datetime.now()).days
        }
    
    def get_all_quota_status(self) -> Dict:
        """Get quota status for all APIs"""
        status = {}
        for api_name in self.monthly_limits.keys():
            status[api_name] = self.get_quota_status(api_name)
        return status
    
    def set_monthly_limit(self, api_name: str, limit: int):
        """Set or update monthly limit for an API"""
        self.monthly_limits[api_name] = limit
        if api_name in self.quotas:
            self.quotas[api_name]['limit'] = limit
        logger.info(f"Set monthly limit for {api_name} to {limit}")
    
    def reset_quota(self, api_name: str):
        """Manually reset quota for an API (for testing/admin purposes)"""
        if api_name in self.quotas:
            self.quotas[api_name]['used'] = 0
            self.quotas[api_name]['reset_date'] = self._get_next_month_start()
            self._save_quotas()
            logger.info(f"Manually reset quota for {api_name}")


# Global quota manager instance
quota_manager = QuotaManager()