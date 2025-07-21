#!/usr/bin/env python3
"""
Configuration Validator
Validates configuration settings and provides safe defaults
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates and sanitizes configuration settings"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate configuration and return sanitized version
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, sanitized_config)
        """
        self.errors = []
        self.warnings = []
        
        # Validate each section
        self._validate_weight_sensor(config.get('weight_sensor', {}))
        self._validate_servo(config.get('servo', {}))
        self._validate_feeding_schedules(config.get('feeding_schedules', []))
        self._validate_weight_thresholds(config.get('weight_thresholds', {}))
        self._validate_web_interface(config.get('web_interface', {}))
        self._validate_database(config.get('database', {}))
        self._validate_logging(config.get('logging', {}))
        self._validate_safety(config.get('safety', {}))
        self._validate_notifications(config.get('notifications', {}))
        self._validate_maintenance(config.get('maintenance', {}))
        
        # Create sanitized config with defaults
        sanitized_config = self._create_sanitized_config(config)
        
        # Log validation results
        if self.errors:
            for error in self.errors:
                logger.error(f"Config validation error: {error}")
        
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Config validation warning: {warning}")
        
        return len(self.errors) == 0, sanitized_config
    
    def _validate_weight_sensor(self, config: Dict[str, Any]):
        """Validate weight sensor configuration"""
        # GPIO pins
        if not isinstance(config.get('dout_pin'), int) or config['dout_pin'] < 1 or config['dout_pin'] > 40:
            self.errors.append("Invalid dout_pin: must be integer 1-40")
        
        if not isinstance(config.get('sck_pin'), int) or config['sck_pin'] < 1 or config['sck_pin'] > 40:
            self.errors.append("Invalid sck_pin: must be integer 1-40")
        
        # Calibration factor
        if not isinstance(config.get('calibration_factor'), (int, float)) or config['calibration_factor'] <= 0:
            self.errors.append("Invalid calibration_factor: must be positive number")
        
        # Sample counts
        if not isinstance(config.get('tare_samples'), int) or config['tare_samples'] < 1 or config['tare_samples'] > 50:
            self.warnings.append("tare_samples should be 1-50, using default")
        
        if not isinstance(config.get('reading_samples'), int) or config['reading_samples'] < 1 or config['reading_samples'] > 20:
            self.warnings.append("reading_samples should be 1-20, using default")
    
    def _validate_servo(self, config: Dict[str, Any]):
        """Validate servo configuration"""
        # GPIO pin
        if not isinstance(config.get('pin'), int) or config['pin'] < 1 or config['pin'] > 40:
            self.errors.append("Invalid servo pin: must be integer 1-40")
        
        # Angles
        if not isinstance(config.get('min_angle'), int) or config['min_angle'] < 0 or config['min_angle'] > 180:
            self.errors.append("Invalid min_angle: must be 0-180")
        
        if not isinstance(config.get('max_angle'), int) or config['max_angle'] < 0 or config['max_angle'] > 180:
            self.errors.append("Invalid max_angle: must be 0-180")
        
        if not isinstance(config.get('feeding_angle'), int) or config['feeding_angle'] < 0 or config['feeding_angle'] > 180:
            self.errors.append("Invalid feeding_angle: must be 0-180")
        
        # Dispensing parameters
        if not isinstance(config.get('portion_grams_per_second'), (int, float)) or config['portion_grams_per_second'] <= 0:
            self.errors.append("Invalid portion_grams_per_second: must be positive")
        
        if not isinstance(config.get('min_dispense_time'), (int, float)) or config['min_dispense_time'] < 0:
            self.errors.append("Invalid min_dispense_time: must be non-negative")
        
        if not isinstance(config.get('max_dispense_time'), (int, float)) or config['max_dispense_time'] <= 0:
            self.errors.append("Invalid max_dispense_time: must be positive")
    
    def _validate_feeding_schedules(self, schedules: List[Dict[str, Any]]):
        """Validate feeding schedules"""
        if not isinstance(schedules, list):
            self.errors.append("feeding_schedules must be a list")
            return
        
        for i, schedule in enumerate(schedules):
            if not isinstance(schedule, dict):
                self.errors.append(f"Schedule {i} must be a dictionary")
                continue
            
            # Time format
            time_str = schedule.get('time', '')
            if not self._is_valid_time_format(time_str):
                self.errors.append(f"Invalid time format in schedule {i}: {time_str}")
            
            # Portion size
            portion = schedule.get('portion', 0)
            if not isinstance(portion, (int, float)) or portion <= 0 or portion > 200:
                self.errors.append(f"Invalid portion in schedule {i}: must be 1-200g")
            
            # Enabled flag
            if not isinstance(schedule.get('enabled'), bool):
                self.warnings.append(f"Schedule {i} enabled flag should be boolean")
    
    def _validate_weight_thresholds(self, config: Dict[str, Any]):
        """Validate weight thresholds"""
        # Cat weight range
        min_weight = config.get('min_cat_weight', 0)
        max_weight = config.get('max_cat_weight', 0)
        
        if not isinstance(min_weight, (int, float)) or min_weight < 0:
            self.errors.append("Invalid min_cat_weight: must be non-negative")
        
        if not isinstance(max_weight, (int, float)) or max_weight <= 0:
            self.errors.append("Invalid max_cat_weight: must be positive")
        
        if min_weight >= max_weight:
            self.errors.append("min_cat_weight must be less than max_cat_weight")
        
        # Tare threshold
        tare_threshold = config.get('tare_threshold', 0)
        if not isinstance(tare_threshold, (int, float)) or tare_threshold < 0:
            self.errors.append("Invalid tare_threshold: must be non-negative")
    
    def _validate_web_interface(self, config: Dict[str, Any]):
        """Validate web interface configuration"""
        # Host
        host = config.get('host', '')
        if not isinstance(host, str) or not host:
            self.errors.append("Invalid web interface host")
        
        # Port
        port = config.get('port', 0)
        if not isinstance(port, int) or port < 1 or port > 65535:
            self.errors.append("Invalid web interface port: must be 1-65535")
        
        # Secret key
        secret_key = config.get('secret_key', '')
        if not isinstance(secret_key, str) or len(secret_key) < 16:
            self.warnings.append("Secret key should be at least 16 characters long")
    
    def _validate_database(self, config: Dict[str, Any]):
        """Validate database configuration"""
        # Path
        path = config.get('path', '')
        if not isinstance(path, str) or not path:
            self.errors.append("Invalid database path")
        
        # Backup interval
        backup_interval = config.get('backup_interval_hours', 0)
        if not isinstance(backup_interval, int) or backup_interval < 1:
            self.warnings.append("backup_interval_hours should be at least 1")
        
        # Cleanup days
        cleanup_days = config.get('cleanup_days', 0)
        if not isinstance(cleanup_days, int) or cleanup_days < 1:
            self.warnings.append("cleanup_days should be at least 1")
    
    def _validate_logging(self, config: Dict[str, Any]):
        """Validate logging configuration"""
        # Level
        level = config.get('level', '')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            self.errors.append(f"Invalid log level: {level}. Must be one of {valid_levels}")
        
        # File
        log_file = config.get('file', '')
        if not isinstance(log_file, str) or not log_file:
            self.errors.append("Invalid log file path")
        
        # Max size
        max_size = config.get('max_size_mb', 0)
        if not isinstance(max_size, (int, float)) or max_size <= 0:
            self.warnings.append("max_size_mb should be positive")
    
    def _validate_safety(self, config: Dict[str, Any]):
        """Validate safety configuration"""
        # Emergency stop pin
        emergency_pin = config.get('emergency_stop_pin', 0)
        if not isinstance(emergency_pin, int) or emergency_pin < 1 or emergency_pin > 40:
            self.errors.append("Invalid emergency_stop_pin: must be integer 1-40")
        
        # Daily feeding limit
        max_daily = config.get('max_daily_feedings', 0)
        if not isinstance(max_daily, int) or max_daily < 1 or max_daily > 50:
            self.warnings.append("max_daily_feedings should be 1-50")
        
        # Feeding interval
        min_interval = config.get('min_feeding_interval_minutes', 0)
        if not isinstance(min_interval, int) or min_interval < 0:
            self.warnings.append("min_feeding_interval_minutes should be non-negative")
        
        # Max portion
        max_portion = config.get('max_portion_grams', 0)
        if not isinstance(max_portion, (int, float)) or max_portion <= 0:
            self.warnings.append("max_portion_grams should be positive")
    
    def _validate_notifications(self, config: Dict[str, Any]):
        """Validate notification configuration"""
        # Email settings
        email_config = config.get('email', {})
        if config.get('enabled', False):
            if not email_config.get('smtp_server'):
                self.warnings.append("SMTP server required for email notifications")
            
            if not email_config.get('username') or not email_config.get('password'):
                self.warnings.append("Email credentials required for notifications")
    
    def _validate_maintenance(self, config: Dict[str, Any]):
        """Validate maintenance configuration"""
        # Auto restart
        auto_restart = config.get('auto_restart_hours', 0)
        if not isinstance(auto_restart, int) or auto_restart < 0:
            self.warnings.append("auto_restart_hours should be non-negative")
        
        # Health check interval
        health_check = config.get('health_check_interval_minutes', 0)
        if not isinstance(health_check, int) or health_check < 1:
            self.warnings.append("health_check_interval_minutes should be at least 1")
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in HH:MM format"""
        try:
            if not isinstance(time_str, str):
                return False
            
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, TypeError):
            return False
    
    def _create_sanitized_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create sanitized configuration with defaults"""
        sanitized = config.copy()
        
        # Add missing sections with defaults
        defaults = {
            'weight_sensor': {
                'dout_pin': 5,
                'sck_pin': 6,
                'calibration_factor': 2280.0,
                'tare_samples': 10,
                'reading_samples': 3,
                'smoothing_samples': 10,
                'stability_threshold': 0.05
            },
            'servo': {
                'pin': 18,
                'min_angle': 0,
                'max_angle': 180,
                'feeding_angle': 90,
                'frequency': 50,
                'portion_grams_per_second': 10,
                'min_dispense_time': 0.5,
                'max_dispense_time': 5.0
            },
            'feeding_schedules': [
                {'time': '08:00', 'portion': 50, 'enabled': True, 'name': 'Breakfast'},
                {'time': '12:00', 'portion': 50, 'enabled': True, 'name': 'Lunch'},
                {'time': '18:00', 'portion': 50, 'enabled': True, 'name': 'Dinner'}
            ],
            'weight_thresholds': {
                'min_cat_weight': 2.0,
                'max_cat_weight': 8.0,
                'tare_threshold': 0.1,
                'cat_detection_delay': 2.0
            },
            'web_interface': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'secret_key': 'change-this-secret-key-in-production',
                'session_timeout': 3600
            },
            'database': {
                'path': 'cat_feeder.db',
                'backup_interval_hours': 24,
                'cleanup_days': 30,
                'max_log_size_mb': 100
            },
            'logging': {
                'level': 'INFO',
                'file': 'cat_feeder.log',
                'max_size_mb': 10,
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'safety': {
                'emergency_stop_pin': 27,
                'max_daily_feedings': 10,
                'min_feeding_interval_minutes': 120,
                'max_portion_grams': 200,
                'low_food_alert_threshold': 100
            },
            'notifications': {
                'enabled': False,
                'email': {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'recipients': []
                },
                'webhook': {
                    'url': '',
                    'enabled': False
                }
            },
            'maintenance': {
                'auto_restart_hours': 168,
                'health_check_interval_minutes': 30,
                'calibration_reminder_days': 30
            }
        }
        
        # Merge defaults with provided config
        for section, default_values in defaults.items():
            if section not in sanitized:
                sanitized[section] = default_values
            else:
                # Merge nested dictionaries
                if isinstance(default_values, dict):
                    for key, default_value in default_values.items():
                        if key not in sanitized[section]:
                            sanitized[section][key] = default_value
        
        return sanitized

def validate_config_file(config_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate configuration file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Tuple of (is_valid, config_dict)
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        validator = ConfigValidator()
        return validator.validate_config(config)
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return False, {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return False, {}
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        return False, {} 