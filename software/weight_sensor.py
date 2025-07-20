#!/usr/bin/env python3
"""
Weight Sensor Interface
Handles HX711 load cell amplifier for weight measurements
"""

import time
import logging
import threading
from typing import Optional, Tuple

try:
    import RPi.GPIO as GPIO
    from hx711 import HX711
except ImportError:
    # Mock for development/testing
    GPIO = None
    HX711 = None

logger = logging.getLogger(__name__)

class WeightSensor:
    def __init__(self, dout_pin: int, sck_pin: int, calibration_factor: float = 2280.0):
        """
        Initialize weight sensor
        
        Args:
            dout_pin: GPIO pin for HX711 data output
            sck_pin: GPIO pin for HX711 serial clock
            calibration_factor: Calibration factor for weight conversion
        """
        self.dout_pin = dout_pin
        self.sck_pin = sck_pin
        self.calibration_factor = calibration_factor
        self.hx711 = None
        self.tare_value = 0
        self.is_calibrated = False
        self.lock = threading.Lock()
        
        # Weight smoothing
        self.weight_history = []
        self.max_history_size = 10
        
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """Initialize the HX711 sensor"""
        try:
            if GPIO is None or HX711 is None:
                logger.warning("GPIO/HX711 not available - using mock sensor")
                return
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.dout_pin, GPIO.IN)
            GPIO.setup(self.sck_pin, GPIO.OUT)
            
            # Initialize HX711
            self.hx711 = HX711(self.dout_pin, self.sck_pin)
            self.hx711.set_reading_format("MSB", "MSB")
            self.hx711.set_reference_unit(self.calibration_factor)
            
            # Reset and tare
            self.hx711.reset()
            self.tare()
            
            logger.info("Weight sensor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize weight sensor: {e}")
            self.hx711 = None
    
    def tare(self, samples: int = 10):
        """
        Tare the scale (set zero point)
        
        Args:
            samples: Number of samples to average for tare
        """
        try:
            if self.hx711 is None:
                logger.warning("Cannot tare - sensor not initialized")
                return False
            
            with self.lock:
                self.hx711.tare(samples)
                self.tare_value = self.hx711.get_tare()
                self.is_calibrated = True
                logger.info(f"Scale tared with {samples} samples")
                return True
                
        except Exception as e:
            logger.error(f"Failed to tare scale: {e}")
            return False
    
    def get_weight(self, samples: int = 3) -> Optional[float]:
        """
        Get current weight reading
        
        Args:
            samples: Number of samples to average
            
        Returns:
            Weight in kilograms, or None if error
        """
        try:
            if self.hx711 is None:
                # Return mock weight for testing
                return self._get_mock_weight()
            
            with self.lock:
                # Get raw reading
                raw_value = self.hx711.get_weight(samples)
                
                if raw_value is None:
                    return None
                
                # Convert to kilograms
                weight_kg = raw_value / 1000.0  # Convert grams to kg
                
                # Apply smoothing
                weight_kg = self._smooth_weight(weight_kg)
                
                return weight_kg
                
        except Exception as e:
            logger.error(f"Error reading weight: {e}")
            return None
    
    def _smooth_weight(self, weight: float) -> float:
        """Apply smoothing to weight readings"""
        self.weight_history.append(weight)
        
        # Keep only recent readings
        if len(self.weight_history) > self.max_history_size:
            self.weight_history.pop(0)
        
        # Return average of recent readings
        if len(self.weight_history) > 0:
            return sum(self.weight_history) / len(self.weight_history)
        
        return weight
    
    def _get_mock_weight(self) -> float:
        """Get mock weight for testing (when GPIO not available)"""
        import random
        # Simulate cat weight between 3-6 kg
        base_weight = 4.5
        noise = random.uniform(-0.5, 0.5)
        return max(0, base_weight + noise)
    
    def calibrate(self, known_weight_grams: float) -> bool:
        """
        Calibrate the sensor with a known weight
        
        Args:
            known_weight_grams: Known weight in grams
            
        Returns:
            True if calibration successful
        """
        try:
            if self.hx711 is None:
                logger.warning("Cannot calibrate - sensor not initialized")
                return False
            
            logger.info(f"Calibrating with known weight: {known_weight_grams}g")
            
            with self.lock:
                # Get current reading
                current_reading = self.hx711.get_raw_data(5)
                if current_reading is None:
                    logger.error("Failed to get raw reading for calibration")
                    return False
                
                # Calculate new calibration factor
                new_factor = current_reading / known_weight_grams
                self.calibration_factor = new_factor
                
                # Update HX711
                self.hx711.set_reference_unit(new_factor)
                
                # Reset and tare
                self.hx711.reset()
                self.tare()
                
                logger.info(f"Calibration successful - new factor: {new_factor:.2f}")
                return True
                
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
    
    def get_calibration_data(self) -> Tuple[float, float]:
        """
        Get calibration data
        
        Returns:
            Tuple of (calibration_factor, tare_value)
        """
        return self.calibration_factor, self.tare_value
    
    def set_calibration_data(self, calibration_factor: float, tare_value: float):
        """
        Set calibration data
        
        Args:
            calibration_factor: Calibration factor
            tare_value: Tare value
        """
        self.calibration_factor = calibration_factor
        self.tare_value = tare_value
        
        if self.hx711 is not None:
            self.hx711.set_reference_unit(calibration_factor)
    
    def is_stable(self, threshold: float = 0.05) -> bool:
        """
        Check if weight reading is stable
        
        Args:
            threshold: Weight change threshold in kg
            
        Returns:
            True if weight is stable
        """
        if len(self.weight_history) < 3:
            return False
        
        recent_weights = self.weight_history[-3:]
        max_diff = max(recent_weights) - min(recent_weights)
        
        return max_diff <= threshold
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            if self.hx711 is not None:
                self.hx711.power_down()
                self.hx711.power_up()
            
            if GPIO is not None:
                GPIO.cleanup([self.dout_pin, self.sck_pin])
                
            logger.info("Weight sensor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class WeightCalibrator:
    """Helper class for weight sensor calibration"""
    
    def __init__(self, weight_sensor: WeightSensor):
        self.weight_sensor = weight_sensor
    
    def interactive_calibration(self):
        """Interactive calibration process"""
        print("=== Weight Sensor Calibration ===")
        print("1. Place known weight on scale")
        print("2. Enter weight in grams")
        print("3. Wait for stable reading")
        print("4. Confirm calibration")
        
        try:
            # Get known weight
            known_weight = float(input("Enter known weight in grams: "))
            
            # Wait for stable reading
            print("Place weight on scale and wait for stable reading...")
            time.sleep(3)
            
            # Check if stable
            if not self.weight_sensor.is_stable():
                print("Warning: Weight reading not stable. Continue anyway? (y/n): ")
                if input().lower() != 'y':
                    return False
            
            # Perform calibration
            success = self.weight_sensor.calibrate(known_weight)
            
            if success:
                print("Calibration successful!")
                return True
            else:
                print("Calibration failed!")
                return False
                
        except ValueError:
            print("Invalid weight value")
            return False
        except KeyboardInterrupt:
            print("\nCalibration cancelled")
            return False
    
    def test_calibration(self, test_weights: list) -> bool:
        """
        Test calibration with multiple known weights
        
        Args:
            test_weights: List of known weights in grams
            
        Returns:
            True if all tests pass
        """
        print("=== Testing Calibration ===")
        
        for i, known_weight in enumerate(test_weights, 1):
            print(f"\nTest {i}: Place {known_weight}g weight on scale")
            input("Press Enter when ready...")
            
            # Get reading
            measured_weight = self.weight_sensor.get_weight()
            if measured_weight is None:
                print("Failed to get weight reading")
                return False
            
            measured_grams = measured_weight * 1000
            error = abs(measured_grams - known_weight)
            error_percent = (error / known_weight) * 100
            
            print(f"Measured: {measured_grams:.1f}g")
            print(f"Expected: {known_weight:.1f}g")
            print(f"Error: {error:.1f}g ({error_percent:.1f}%)")
            
            if error_percent > 5:  # 5% tolerance
                print("Error too high - calibration may need adjustment")
                return False
        
        print("\nAll calibration tests passed!")
        return True 