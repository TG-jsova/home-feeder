#!/usr/bin/env python3
"""
Automated Cat Feeder - Main Application
Controls the entire system including weight sensing, feeding, and web interface
"""

import time
import threading
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from feeder_controller import FeederController
from weight_sensor import WeightSensor
from web_interface import WebInterface
from database import Database
from config_validator import validate_config_file
from health_monitor import HealthMonitor
from backup_restore import BackupManager

# Configure logging
def setup_logging(config):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', 'cat_feeder.log')
    max_size = log_config.get('max_size_mb', 10) * 1024 * 1024  # Convert to bytes
    backup_count = log_config.get('backup_count', 5)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_size, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler]
    )

logger = logging.getLogger(__name__)

class CatFeeder:
    def __init__(self):
        """Initialize the cat feeder system"""
        # Load and validate configuration
        self.config = self.load_config()
        setup_logging(self.config)
        
        self.running = False
        
        # Initialize components
        self.database = Database()
        self.weight_sensor = WeightSensor(
            dout_pin=self.config['weight_sensor']['dout_pin'],
            sck_pin=self.config['weight_sensor']['sck_pin'],
            calibration_factor=self.config['weight_sensor']['calibration_factor']
        )
        self.feeder_controller = FeederController(
            servo_pin=self.config['servo']['pin'],
            servo_min_angle=self.config['servo']['min_angle'],
            servo_max_angle=self.config['servo']['max_angle']
        )
        self.web_interface = WebInterface(self)
        
        # Initialize health monitor and backup manager
        self.health_monitor = HealthMonitor(self.database, self.config)
        self.backup_manager = BackupManager(self.config)
        
        # Feeding state
        self.last_feeding_time = None
        self.current_weight = 0.0
        self.feeding_schedules = self.config['feeding_schedules']
        
        # Safety tracking
        self.daily_feeding_count = 0
        self.last_feeding_date = None
        
        logger.info("Cat Feeder initialized successfully")
    
    def load_config(self):
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent / 'config.json'
        if config_path.exists():
            # Validate configuration
            is_valid, config = validate_config_file(str(config_path))
            if not is_valid:
                logger.error("Configuration validation failed, using defaults")
                return self._create_default_config(config_path)
            return config
        else:
            return self._create_default_config(config_path)
    
    def _create_default_config(self, config_path: Path):
        """Create default configuration file"""
        # Default configuration
        default_config = {
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
                'min_cat_weight': 2.0,  # kg
                'max_cat_weight': 8.0,  # kg
                'tare_threshold': 0.1,   # kg
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
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info("Default configuration created")
        return default_config
    
    def start(self):
        """Start the cat feeder system"""
        if self.running:
            logger.warning("Cat feeder is already running")
            return
        
        self.running = True
        logger.info("Starting cat feeder system...")
        
        # Start health monitoring
        self.health_monitor.start()
        
        # Start weight monitoring thread
        weight_thread = threading.Thread(target=self.weight_monitoring_loop, daemon=True)
        weight_thread.start()
        
        # Start feeding schedule thread
        schedule_thread = threading.Thread(target=self.feeding_schedule_loop, daemon=True)
        schedule_thread.start()
        
        # Start maintenance thread
        maintenance_thread = threading.Thread(target=self.maintenance_loop, daemon=True)
        maintenance_thread.start()
        
        # Start web interface
        web_thread = threading.Thread(target=self.web_interface.start, daemon=True)
        web_thread.start()
        
        logger.info("Cat feeder system started successfully")
        
        try:
            # Main loop
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            self.stop()
    
    def stop(self):
        """Stop the cat feeder system"""
        logger.info("Stopping cat feeder system...")
        self.running = False
        
        # Stop health monitoring
        self.health_monitor.stop()
        
        # Cleanup components
        self.feeder_controller.cleanup()
        self.web_interface.stop()
        
        logger.info("Cat feeder system stopped")
    
    def weight_monitoring_loop(self):
        """Continuous weight monitoring loop"""
        while self.running:
            try:
                weight = self.weight_sensor.get_weight()
                if weight is not None:
                    self.current_weight = weight
                    
                    # Check if cat is present
                    if self.is_cat_present():
                        logger.info(f"Cat detected - Weight: {weight:.2f}kg")
                        self.handle_cat_detection()
                
                time.sleep(0.5)  # Update every 500ms
                
            except Exception as e:
                logger.error(f"Error in weight monitoring: {e}")
                time.sleep(1)
    
    def feeding_schedule_loop(self):
        """Check feeding schedules and trigger feedings"""
        while self.running:
            try:
                current_time = datetime.now().strftime('%H:%M')
                
                for schedule in self.feeding_schedules:
                    if (schedule['enabled'] and 
                        schedule['time'] == current_time and
                        self.should_feed()):
                        
                        logger.info(f"Triggering scheduled feeding at {current_time}")
                        self.feed_cat(schedule['portion'])
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in feeding schedule: {e}")
                time.sleep(60)
    
    def is_cat_present(self):
        """Check if a cat is present on the scale"""
        min_weight = self.config['weight_thresholds']['min_cat_weight']
        max_weight = self.config['weight_thresholds']['max_cat_weight']
        tare_threshold = self.config['weight_thresholds']['tare_threshold']
        
        return (self.current_weight > tare_threshold and 
                min_weight <= self.current_weight <= max_weight)
    
    def should_feed(self):
        """Determine if feeding should occur based on time since last feeding"""
        if self.last_feeding_time is None:
            return True
        
        # Check daily feeding limit
        current_date = datetime.now().date()
        if self.last_feeding_date != current_date:
            self.daily_feeding_count = 0
            self.last_feeding_date = current_date
        
        max_daily = self.config['safety']['max_daily_feedings']
        if self.daily_feeding_count >= max_daily:
            logger.warning(f"Daily feeding limit reached ({max_daily})")
            return False
        
        # Check minimum interval
        min_interval = timedelta(minutes=self.config['safety']['min_feeding_interval_minutes'])
        time_since_last = datetime.now() - self.last_feeding_time
        
        return time_since_last >= min_interval
    
    def handle_cat_detection(self):
        """Handle cat detection events"""
        # Log cat detection
        self.database.log_event('cat_detected', {
            'weight': self.current_weight,
            'timestamp': datetime.now().isoformat()
        })
        
        # Could trigger automatic feeding based on weight
        # or other criteria here
    
    def feed_cat(self, portion_grams):
        """Feed the cat with specified portion"""
        try:
            # Validate portion size
            max_portion = self.config['safety']['max_portion_grams']
            if portion_grams > max_portion:
                logger.error(f"Portion size {portion_grams}g exceeds maximum {max_portion}g")
                return False
            
            logger.info(f"Feeding cat {portion_grams}g of food")
            
            # Dispense food
            success = self.feeder_controller.dispense_food(portion_grams)
            
            if success:
                self.last_feeding_time = datetime.now()
                self.daily_feeding_count += 1
                
                # Log feeding event
                self.database.log_event('feeding', {
                    'portion': portion_grams,
                    'timestamp': self.last_feeding_time.isoformat(),
                    'cat_weight': self.current_weight,
                    'daily_count': self.daily_feeding_count
                })
                
                logger.info(f"Successfully fed {portion_grams}g of food (daily count: {self.daily_feeding_count})")
                return True
            else:
                logger.error("Failed to dispense food")
                return False
                
        except Exception as e:
            logger.error(f"Error during feeding: {e}")
            return False
    
    def get_status(self):
        """Get current system status"""
        return {
            'running': self.running,
            'current_weight': self.current_weight,
            'last_feeding_time': self.last_feeding_time.isoformat() if self.last_feeding_time else None,
            'cat_present': self.is_cat_present(),
            'feeding_schedules': self.feeding_schedules,
            'daily_feeding_count': self.daily_feeding_count,
            'health_status': self.health_monitor.get_health_status()
        }
    
    def update_config(self, new_config):
        """Update system configuration"""
        self.config.update(new_config)
        
        # Save to file
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info("Configuration updated")
    
    def maintenance_loop(self):
        """Maintenance tasks loop"""
        while self.running:
            try:
                # Database cleanup
                self.database.cleanup_old_data(self.config['database']['cleanup_days'])
                
                # Create backup if needed
                self._check_backup_schedule()
                
                # Check for auto-restart
                self._check_auto_restart()
                
                # Sleep for maintenance interval
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")
                time.sleep(3600)
    
    def _check_backup_schedule(self):
        """Check if backup is due"""
        try:
            backup_interval = self.config['database']['backup_interval_hours']
            last_backup_file = self.backup_manager.list_backups()
            
            if not last_backup_file:
                # No backups exist, create one
                self.backup_manager.create_backup()
                return
            
            # Check if enough time has passed since last backup
            last_backup = last_backup_file[0]  # Most recent
            last_backup_time = datetime.fromisoformat(last_backup['created'])
            time_since_backup = datetime.now() - last_backup_time
            
            if time_since_backup.total_seconds() >= backup_interval * 3600:
                self.backup_manager.create_backup()
                logger.info("Scheduled backup created")
                
        except Exception as e:
            logger.error(f"Error checking backup schedule: {e}")
    
    def _check_auto_restart(self):
        """Check if auto-restart is needed"""
        try:
            auto_restart_hours = self.config['maintenance']['auto_restart_hours']
            if auto_restart_hours <= 0:
                return
            
            # Get system uptime
            import psutil
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600
            
            if uptime_hours >= auto_restart_hours:
                logger.info(f"Auto-restart triggered after {uptime_hours:.1f} hours")
                self._schedule_restart()
                
        except Exception as e:
            logger.error(f"Error checking auto-restart: {e}")
    
    def _schedule_restart(self):
        """Schedule system restart"""
        try:
            import subprocess
            # Schedule restart in 5 minutes
            subprocess.run(['shutdown', '-r', '+5'], check=True)
            logger.info("System restart scheduled in 5 minutes")
            
            # Log restart event
            self.database.log_event('system_restart', {
                'scheduled_time': (datetime.now() + timedelta(minutes=5)).isoformat(),
                'reason': 'auto_restart'
            })
            
        except Exception as e:
            logger.error(f"Failed to schedule restart: {e}")
    
    def create_backup(self, include_logs: bool = True, include_database: bool = True) -> str:
        """Create a backup of the system"""
        try:
            backup_path = self.backup_manager.create_backup(include_logs, include_database)
            logger.info(f"Manual backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get list of available backups"""
        return self.backup_manager.list_backups()
    
    def restore_backup(self, backup_path: str, restore_database: bool = True, 
                      restore_config: bool = True, restore_logs: bool = False) -> bool:
        """Restore from backup"""
        try:
            success = self.backup_manager.restore_backup(backup_path, restore_database, 
                                                        restore_config, restore_logs)
            if success:
                logger.info(f"Backup restored successfully: {backup_path}")
            return success
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

def main():
    """Main entry point"""
    feeder = CatFeeder()
    
    try:
        feeder.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        feeder.stop()

if __name__ == "__main__":
    main() 