#!/usr/bin/env python3
"""
Automated Cat Feeder - Main Application
Controls the entire system including weight sensing, feeding, and web interface
"""

import time
import threading
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from feeder_controller import FeederController
from weight_sensor import WeightSensor
from web_interface import WebInterface
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cat_feeder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CatFeeder:
    def __init__(self):
        """Initialize the cat feeder system"""
        self.config = self.load_config()
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
        
        # Feeding state
        self.last_feeding_time = None
        self.current_weight = 0.0
        self.feeding_schedules = self.config['feeding_schedules']
        
        logger.info("Cat Feeder initialized successfully")
    
    def load_config(self):
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                'weight_sensor': {
                    'dout_pin': 5,
                    'sck_pin': 6,
                    'calibration_factor': 2280.0
                },
                'servo': {
                    'pin': 18,
                    'min_angle': 0,
                    'max_angle': 180,
                    'feeding_angle': 90
                },
                'feeding_schedules': [
                    {'time': '08:00', 'portion': 50, 'enabled': True},
                    {'time': '12:00', 'portion': 50, 'enabled': True},
                    {'time': '18:00', 'portion': 50, 'enabled': True}
                ],
                'weight_thresholds': {
                    'min_cat_weight': 2.0,  # kg
                    'max_cat_weight': 8.0,  # kg
                    'tare_threshold': 0.1   # kg
                },
                'web_interface': {
                    'host': '0.0.0.0',
                    'port': 5000
                }
            }
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def start(self):
        """Start the cat feeder system"""
        if self.running:
            logger.warning("Cat feeder is already running")
            return
        
        self.running = True
        logger.info("Starting cat feeder system...")
        
        # Start weight monitoring thread
        weight_thread = threading.Thread(target=self.weight_monitoring_loop, daemon=True)
        weight_thread.start()
        
        # Start feeding schedule thread
        schedule_thread = threading.Thread(target=self.feeding_schedule_loop, daemon=True)
        schedule_thread.start()
        
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
        
        min_interval = timedelta(hours=2)  # Minimum 2 hours between feedings
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
            logger.info(f"Feeding cat {portion_grams}g of food")
            
            # Dispense food
            success = self.feeder_controller.dispense_food(portion_grams)
            
            if success:
                self.last_feeding_time = datetime.now()
                
                # Log feeding event
                self.database.log_event('feeding', {
                    'portion': portion_grams,
                    'timestamp': self.last_feeding_time.isoformat(),
                    'cat_weight': self.current_weight
                })
                
                logger.info(f"Successfully fed {portion_grams}g of food")
            else:
                logger.error("Failed to dispense food")
                
        except Exception as e:
            logger.error(f"Error during feeding: {e}")
    
    def get_status(self):
        """Get current system status"""
        return {
            'running': self.running,
            'current_weight': self.current_weight,
            'last_feeding_time': self.last_feeding_time.isoformat() if self.last_feeding_time else None,
            'cat_present': self.is_cat_present(),
            'feeding_schedules': self.feeding_schedules
        }
    
    def update_config(self, new_config):
        """Update system configuration"""
        self.config.update(new_config)
        
        # Save to file
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info("Configuration updated")

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