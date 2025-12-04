import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_company_info(self) -> Dict[str, str]:
        return self._config.get('company', {})
    
    def get_invoice_settings(self) -> Dict[str, Any]:
        return self._config.get('invoice', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        return self._config.get('database', {})
    
    def get_output_settings(self) -> Dict[str, str]:
        return self._config.get('output', {})
    
    def get_email_settings(self) -> Dict[str, Any]:
        return self._config.get('email', {})