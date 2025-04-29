import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.default_config = {
            "security": {
                "max_text_length": 10000,
                "max_file_size": 1024 * 1024,
                "rate_limit": 100,
                "allowed_file_types": [".txt"],
                "log_retention_days": 30
            },
            "models": {
                "gpt2": {
                    "model_name": "microsoft/DialogRPT-human-vs-rand",
                    "max_length": 512,
                    "truncation": True
                },
                "roberta": {
                    "model_name": "roberta-base-openai-detector",
                    "max_length": 512,
                    "truncation": True
                }
            },
            "ui": {
                "theme": "light",
                "font_size": 12,
                "window_size": {
                    "width": 800,
                    "height": 600
                },
                "min_window_size": {
                    "width": 600,
                    "height": 400
                }
            },
            "analysis": {
                "confidence_threshold": 0.7,
                "min_text_length": 10,
                "batch_size": 10
            }
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all settings exist
                    return {**self.default_config, **config}
            return self.default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate security settings
            security = self.config['security']
            assert security['max_text_length'] > 0
            assert security['max_file_size'] > 0
            assert security['rate_limit'] > 0
            assert isinstance(security['allowed_file_types'], list)
            
            # Validate model settings
            models = self.config['models']
            for model in models.values():
                assert isinstance(model['model_name'], str)
                assert model['max_length'] > 0
                assert isinstance(model['truncation'], bool)
            
            # Validate UI settings
            ui = self.config['ui']
            assert ui['theme'] in ['light', 'dark']
            assert ui['font_size'] > 0
            assert ui['window_size']['width'] > 0
            assert ui['window_size']['height'] > 0
            
            # Validate analysis settings
            analysis = self.config['analysis']
            assert 0 <= analysis['confidence_threshold'] <= 1
            assert analysis['min_text_length'] > 0
            assert analysis['batch_size'] > 0
            
            return True
        except (AssertionError, KeyError) as e:
            print(f"Configuration validation failed: {e}")
            return False 