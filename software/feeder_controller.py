#!/usr/bin/env python3
"""
Feeder Controller
Handles servo motor control for food dispensing
"""

import time
import logging
import threading
from typing import Optional, Dict, Any

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Mock for development/testing
    GPIO = None

logger = logging.getLogger(__name__)

class FeederController:
    def __init__(self, servo_pin: int, servo_min_angle: int = 0, 
                 servo_max_angle: int = 180, feeding_angle: int = 90):
        """
        Initialize feeder controller
        
        Args:
            servo_pin: GPIO pin for servo motor
            servo_min_angle: Minimum servo angle
            servo_max_angle: Maximum servo angle
            feeding_angle: Angle for dispensing food
        """
        self.servo_pin = servo_pin
        self.servo_min_angle = servo_min_angle
        self.servo_max_angle = servo_max_angle
        self.feeding_angle = feeding_angle
        
        # Servo control parameters
        self.frequency = 50  # Hz
        self.duty_cycle_min = 2.5  # %
        self.duty_cycle_max = 12.5  # %
        
        # Feeding parameters
        self.portion_grams_per_second = 10  # grams per second of dispensing
        self.min_dispense_time = 0.5  # seconds
        self.max_dispense_time = 5.0  # seconds
        
        # State
        self.is_dispensing = False
        self.current_angle = 0
        self.pwm = None
        self.lock = threading.Lock()
        
        self._initialize_servo()
    
    def _initialize_servo(self):
        """Initialize the servo motor"""
        try:
            if GPIO is None:
                logger.warning("GPIO not available - using mock servo")
                return
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.servo_pin, GPIO.OUT)
            
            # Setup PWM
            self.pwm = GPIO.PWM(self.servo_pin, self.frequency)
            self.pwm.start(0)
            
            # Move to rest position
            self.set_angle(0)
            time.sleep(1)
            
            logger.info("Servo motor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize servo motor: {e}")
            self.pwm = None
    
    def set_angle(self, angle: int) -> bool:
        """
        Set servo angle
        
        Args:
            angle: Target angle (0-180)
            
        Returns:
            True if successful
        """
        try:
            # Clamp angle to valid range
            angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
            
            if self.pwm is None:
                logger.warning("Cannot set angle - servo not initialized")
                return False
            
            with self.lock:
                # Convert angle to duty cycle
                duty_cycle = self._angle_to_duty_cycle(angle)
                
                # Set PWM duty cycle
                self.pwm.ChangeDutyCycle(duty_cycle)
                self.current_angle = angle
                
                logger.debug(f"Servo set to {angle}° (duty cycle: {duty_cycle:.1f}%)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to set servo angle: {e}")
            return False
    
    def _angle_to_duty_cycle(self, angle: int) -> float:
        """Convert angle to PWM duty cycle"""
        # Map angle (0-180) to duty cycle (2.5%-12.5%)
        duty_cycle = (angle / 180.0) * (self.duty_cycle_max - self.duty_cycle_min) + self.duty_cycle_min
        return duty_cycle
    
    def dispense_food(self, portion_grams: float) -> bool:
        """
        Dispense a specific portion of food
        
        Args:
            portion_grams: Amount to dispense in grams
            
        Returns:
            True if dispensing successful
        """
        try:
            if self.is_dispensing:
                logger.warning("Already dispensing food")
                return False
            
            # Calculate dispense time based on portion
            dispense_time = portion_grams / self.portion_grams_per_second
            dispense_time = max(self.min_dispense_time, min(self.max_dispense_time, dispense_time))
            
            logger.info(f"Dispensing {portion_grams}g of food over {dispense_time:.1f}s")
            
            # Start dispensing in separate thread
            dispense_thread = threading.Thread(
                target=self._dispense_food_thread,
                args=(dispense_time,),
                daemon=True
            )
            dispense_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start food dispensing: {e}")
            return False
    
    def _dispense_food_thread(self, dispense_time: float):
        """Thread function for dispensing food"""
        try:
            self.is_dispensing = True
            
            # Move to feeding position
            if not self.set_angle(self.feeding_angle):
                logger.error("Failed to move servo to feeding position")
                return
            
            # Hold position for dispense time
            time.sleep(dispense_time)
            
            # Return to rest position
            if not self.set_angle(0):
                logger.error("Failed to return servo to rest position")
                return
            
            logger.info("Food dispensing completed")
            
        except Exception as e:
            logger.error(f"Error during food dispensing: {e}")
        finally:
            self.is_dispensing = False
    
    def dispense_food_manual(self, duration_seconds: float) -> bool:
        """
        Manually dispense food for a specific duration
        
        Args:
            duration_seconds: How long to dispense in seconds
            
        Returns:
            True if successful
        """
        try:
            if self.is_dispensing:
                logger.warning("Already dispensing food")
                return False
            
            logger.info(f"Manual dispensing for {duration_seconds}s")
            
            # Start dispensing in separate thread
            dispense_thread = threading.Thread(
                target=self._dispense_food_thread,
                args=(duration_seconds,),
                daemon=True
            )
            dispense_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start manual dispensing: {e}")
            return False
    
    def stop_dispensing(self):
        """Stop current dispensing operation"""
        try:
            if self.is_dispensing:
                logger.info("Stopping food dispensing")
                
                # Return to rest position
                self.set_angle(0)
                self.is_dispensing = False
                
        except Exception as e:
            logger.error(f"Error stopping dispensing: {e}")
    
    def test_servo(self) -> bool:
        """
        Test servo motor movement
        
        Returns:
            True if test successful
        """
        try:
            logger.info("Testing servo motor...")
            
            # Test full range of motion
            test_angles = [0, 45, 90, 135, 180, 90, 0]
            
            for angle in test_angles:
                if not self.set_angle(angle):
                    logger.error(f"Failed to set angle to {angle}°")
                    return False
                time.sleep(0.5)
            
            logger.info("Servo test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Servo test failed: {e}")
            return False
    
    def calibrate_portion(self, known_weight_grams: float, dispense_time: float) -> bool:
        """
        Calibrate portion dispensing rate
        
        Args:
            known_weight_grams: Known weight dispensed
            dispense_time: Time taken to dispense
            
        Returns:
            True if calibration successful
        """
        try:
            if dispense_time <= 0:
                logger.error("Invalid dispense time")
                return False
            
            # Calculate new rate
            new_rate = known_weight_grams / dispense_time
            old_rate = self.portion_grams_per_second
            
            self.portion_grams_per_second = new_rate
            
            logger.info(f"Portion rate calibrated: {old_rate:.1f} -> {new_rate:.1f} g/s")
            return True
            
        except Exception as e:
            logger.error(f"Portion calibration failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current feeder status"""
        return {
            'is_dispensing': self.is_dispensing,
            'current_angle': self.current_angle,
            'portion_rate': self.portion_grams_per_second,
            'servo_initialized': self.pwm is not None
        }
    
    def update_config(self, config: Dict[str, Any]):
        """Update feeder configuration"""
        if 'feeding_angle' in config:
            self.feeding_angle = config['feeding_angle']
        
        if 'portion_grams_per_second' in config:
            self.portion_grams_per_second = config['portion_grams_per_second']
        
        if 'min_dispense_time' in config:
            self.min_dispense_time = config['min_dispense_time']
        
        if 'max_dispense_time' in config:
            self.max_dispense_time = config['max_dispense_time']
        
        logger.info("Feeder configuration updated")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            if self.is_dispensing:
                self.stop_dispensing()
            
            if self.pwm is not None:
                self.pwm.stop()
                self.pwm = None
            
            if GPIO is not None:
                GPIO.cleanup([self.servo_pin])
            
            logger.info("Feeder controller cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class FeederCalibrator:
    """Helper class for feeder calibration"""
    
    def __init__(self, feeder_controller: FeederController):
        self.feeder_controller = feeder_controller
    
    def interactive_calibration(self):
        """Interactive portion calibration"""
        print("=== Feeder Portion Calibration ===")
        print("1. Place empty container on scale")
        print("2. Tare the scale")
        print("3. Start dispensing")
        print("4. Stop dispensing and measure weight")
        print("5. Calculate dispensing rate")
        
        try:
            # Get dispense time
            dispense_time = float(input("Enter dispense time in seconds: "))
            
            # Get dispensed weight
            dispensed_weight = float(input("Enter dispensed weight in grams: "))
            
            # Calibrate
            success = self.feeder_controller.calibrate_portion(dispensed_weight, dispense_time)
            
            if success:
                print("Calibration successful!")
                print(f"New dispensing rate: {self.feeder_controller.portion_grams_per_second:.1f} g/s")
                return True
            else:
                print("Calibration failed!")
                return False
                
        except ValueError:
            print("Invalid input value")
            return False
        except KeyboardInterrupt:
            print("\nCalibration cancelled")
            return False
    
    def test_dispensing(self, test_portions: list) -> bool:
        """
        Test dispensing with multiple portions
        
        Args:
            test_portions: List of portions to test in grams
            
        Returns:
            True if all tests pass
        """
        print("=== Testing Food Dispensing ===")
        
        for i, portion in enumerate(test_portions, 1):
            print(f"\nTest {i}: Dispensing {portion}g")
            input("Press Enter to start dispensing...")
            
            # Start dispensing
            success = self.feeder_controller.dispense_food(portion)
            if not success:
                print("Failed to start dispensing")
                return False
            
            # Wait for completion
            while self.feeder_controller.is_dispensing:
                time.sleep(0.1)
            
            print("Dispensing completed")
            
            # Ask for confirmation
            confirm = input("Did the portion look correct? (y/n): ")
            if confirm.lower() != 'y':
                print("Test failed - portion incorrect")
                return False
        
        print("\nAll dispensing tests passed!")
        return True 