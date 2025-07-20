#!/usr/bin/env python3
"""
System Test Script for Automated Cat Feeder
Tests all components and provides diagnostic information
"""

import time
import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from weight_sensor import WeightSensor, WeightCalibrator
from feeder_controller import FeederController, FeederCalibrator
from database import Database

class SystemTester:
    def __init__(self):
        """Initialize system tester"""
        self.test_results = {}
        self.database = Database()
        
        # Initialize components
        try:
            self.weight_sensor = WeightSensor(dout_pin=5, sck_pin=6)
            self.feeder_controller = FeederController(servo_pin=18)
            print("✓ Components initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize components: {e}")
            sys.exit(1)
    
    def run_all_tests(self):
        """Run all system tests"""
        print("\n=== Automated Cat Feeder System Test ===\n")
        
        tests = [
            ("Weight Sensor", self.test_weight_sensor),
            ("Feeder Controller", self.test_feeder_controller),
            ("Database", self.test_database),
            ("Integration", self.test_integration),
            ("Calibration", self.test_calibration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result['passed']:
                    print(f"✓ {test_name} test passed")
                else:
                    print(f"✗ {test_name} test failed: {result['error']}")
            except Exception as e:
                print(f"✗ {test_name} test error: {e}")
                self.test_results[test_name] = {'passed': False, 'error': str(e)}
        
        self.print_summary()
    
    def test_weight_sensor(self):
        """Test weight sensor functionality"""
        try:
            # Test basic reading
            weight = self.weight_sensor.get_weight()
            if weight is None:
                return {'passed': False, 'error': 'No weight reading'}
            
            print(f"  Current weight: {weight:.3f} kg")
            
            # Test stability
            readings = []
            for i in range(10):
                readings.append(self.weight_sensor.get_weight())
                time.sleep(0.1)
            
            avg_weight = sum(readings) / len(readings)
            max_variation = max(readings) - min(readings)
            
            print(f"  Average weight: {avg_weight:.3f} kg")
            print(f"  Max variation: {max_variation:.3f} kg")
            
            # Check if readings are stable
            if max_variation > 0.1:
                return {'passed': False, 'error': f'Unstable readings (variation: {max_variation:.3f}kg)'}
            
            # Test tare function
            if self.weight_sensor.tare():
                print("  ✓ Tare function working")
            else:
                return {'passed': False, 'error': 'Tare function failed'}
            
            return {'passed': True, 'weight': weight, 'stability': max_variation}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_feeder_controller(self):
        """Test feeder controller functionality"""
        try:
            # Test servo movement
            if self.feeder_controller.test_servo():
                print("  ✓ Servo test passed")
            else:
                return {'passed': False, 'error': 'Servo test failed'}
            
            # Test angle setting
            test_angles = [0, 90, 180, 90, 0]
            for angle in test_angles:
                if not self.feeder_controller.set_angle(angle):
                    return {'passed': False, 'error': f'Failed to set angle {angle}°'}
                time.sleep(0.5)
            
            print("  ✓ Angle control working")
            
            # Test dispensing (brief)
            if self.feeder_controller.dispense_food_manual(0.5):
                print("  ✓ Brief dispensing test passed")
                time.sleep(1)  # Wait for completion
            else:
                return {'passed': False, 'error': 'Dispensing test failed'}
            
            return {'passed': True}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_database(self):
        """Test database functionality"""
        try:
            # Test event logging
            test_event = {
                'test': True,
                'timestamp': time.time()
            }
            
            self.database.log_event('test_event', test_event)
            print("  ✓ Event logging working")
            
            # Test retrieving events
            events = self.database.get_recent_events(5)
            if len(events) > 0:
                print(f"  ✓ Retrieved {len(events)} recent events")
            else:
                return {'passed': False, 'error': 'No events retrieved'}
            
            # Test weight logging
            self.database.log_weight_reading(1.5)
            print("  ✓ Weight logging working")
            
            # Test feeding logging
            self.database.log_feeding(50, 4.2)
            print("  ✓ Feeding logging working")
            
            # Test statistics
            stats = self.database.get_statistics(1)
            print(f"  ✓ Statistics: {stats}")
            
            return {'passed': True, 'events_count': len(events)}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_integration(self):
        """Test component integration"""
        try:
            # Test weight monitoring
            initial_weight = self.weight_sensor.get_weight()
            print(f"  Initial weight: {initial_weight:.3f} kg")
            
            # Simulate cat detection
            if initial_weight and initial_weight > 0.1:
                print("  ✓ Weight sensor detecting load")
            else:
                print("  ⚠ No significant weight detected")
            
            # Test feeding integration
            print("  Testing feeding integration...")
            print("  Place a container under the feeder to catch food")
            input("  Press Enter to continue...")
            
            # Perform test feeding
            if self.feeder_controller.dispense_food(25):  # 25g test
                print("  ✓ Feeding integration working")
                time.sleep(3)  # Wait for completion
            else:
                return {'passed': False, 'error': 'Feeding integration failed'}
            
            return {'passed': True}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_calibration(self):
        """Test calibration functionality"""
        try:
            print("  Testing calibration tools...")
            
            # Test weight calibrator
            weight_calibrator = WeightCalibrator(self.weight_sensor)
            print("  ✓ Weight calibrator initialized")
            
            # Test feeder calibrator
            feeder_calibrator = FeederCalibrator(self.feeder_controller)
            print("  ✓ Feeder calibrator initialized")
            
            # Test calibration data
            cal_factor, tare_value = self.weight_sensor.get_calibration_data()
            print(f"  Current calibration factor: {cal_factor}")
            print(f"  Current tare value: {tare_value}")
            
            return {'passed': True, 'calibration_factor': cal_factor}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def print_summary(self):
        """Print test summary"""
        print("\n=== Test Summary ===")
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"{test_name:20} {status}")
            if result['passed']:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready to use.")
        else:
            print("⚠ Some tests failed. Please check the issues above.")
        
        # Save test results
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print("\nTest results saved to test_results.json")

def interactive_test():
    """Interactive testing mode"""
    print("=== Interactive Testing Mode ===")
    print("This mode allows you to test individual components.")
    
    tester = SystemTester()
    
    while True:
        print("\nAvailable tests:")
        print("1. Weight Sensor Test")
        print("2. Feeder Controller Test")
        print("3. Database Test")
        print("4. Integration Test")
        print("5. Calibration Test")
        print("6. Run All Tests")
        print("0. Exit")
        
        choice = input("\nSelect test (0-6): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            result = tester.test_weight_sensor()
            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
        elif choice == '2':
            result = tester.test_feeder_controller()
            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
        elif choice == '3':
            result = tester.test_database()
            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
        elif choice == '4':
            result = tester.test_integration()
            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
        elif choice == '5':
            result = tester.test_calibration()
            print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
        elif choice == '6':
            tester.run_all_tests()
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_test()
    else:
        tester = SystemTester()
        tester.run_all_tests()

if __name__ == "__main__":
    main() 