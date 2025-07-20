# Calibration Guide - Automated Cat Feeder

## Overview

Proper calibration is essential for accurate weight measurements and precise food dispensing. This guide covers both weight sensor calibration and food dispensing calibration.

## Weight Sensor Calibration

### Understanding the HX711 Load Cell

The HX711 is a 24-bit analog-to-digital converter designed specifically for load cells. It provides:
- High resolution (24-bit)
- Low noise
- Programmable gain
- Simple serial interface

### Calibration Process

#### Step 1: Hardware Setup

1. **Ensure Proper Connections**
   ```
   Load Cell → HX711 → Raspberry Pi
   Red → VCC (5V)
   Black → GND
   White → A+
   Green → A-
   ```

2. **Check Power Supply**
   - Verify 5V supply to HX711
   - Ensure stable voltage
   - Check for noise or fluctuations

#### Step 2: Initial Testing

1. **Test Basic Communication**
   ```python
   from weight_sensor import WeightSensor
   
   sensor = WeightSensor(dout_pin=5, sck_pin=6)
   weight = sensor.get_weight()
   print(f"Raw reading: {weight}")
   ```

2. **Check for Stable Readings**
   - Readings should be consistent when no weight is applied
   - Variations should be minimal (< 0.01kg)
   - If unstable, check connections and power

#### Step 3: Tare Calibration

1. **Remove All Weight**
   - Ensure no objects on the scale
   - Clean the surface
   - Wait for readings to stabilize

2. **Perform Tare**
   ```python
   sensor.tare(samples=10)
   print("Scale tared")
   ```

3. **Verify Tare**
   - Reading should be close to 0.0kg
   - Variations should be minimal
   - If not zero, repeat tare process

#### Step 4: Known Weight Calibration

1. **Prepare Known Weights**
   - Use certified weights if possible
   - Common household items with known weights:
     - 1kg bag of sugar/flour
     - 500g water bottle
     - 250g coffee can
   - Weigh items on a reliable scale first

2. **Interactive Calibration**
   ```python
   from weight_sensor import WeightCalibrator
   
   calibrator = WeightCalibrator(sensor)
   calibrator.interactive_calibration()
   ```

3. **Manual Calibration**
   ```python
   # Place known weight on scale
   known_weight_grams = 1000  # 1kg in grams
   
   # Perform calibration
   success = sensor.calibrate(known_weight_grams)
   if success:
       print("Calibration successful")
   else:
       print("Calibration failed")
   ```

#### Step 5: Verification Testing

1. **Test Multiple Weights**
   ```python
   test_weights = [100, 500, 1000, 2000]  # grams
   calibrator.test_calibration(test_weights)
   ```

2. **Check Accuracy**
   - Test with weights across the full range
   - Verify readings are within ±2% of actual weight
   - Document calibration factor for future reference

### Calibration Factors

#### Typical Values
- **5kg Load Cell**: ~2280
- **10kg Load Cell**: ~2280
- **20kg Load Cell**: ~2280

#### Factors Affecting Calibration
- Load cell sensitivity
- HX711 gain setting
- Mechanical mounting
- Temperature variations

### Troubleshooting Weight Calibration

#### Unstable Readings
**Symptoms**: Readings fluctuate significantly
**Causes**:
- Loose connections
- Power supply noise
- Mechanical vibration
- Temperature changes

**Solutions**:
- Check all wire connections
- Use stable power supply
- Isolate from vibration
- Allow temperature stabilization

#### Inaccurate Readings
**Symptoms**: Readings are consistently wrong
**Causes**:
- Wrong calibration factor
- Mechanical binding
- Load cell damage
- Incorrect wiring

**Solutions**:
- Recalibrate with known weight
- Check mechanical mounting
- Test load cell with multimeter
- Verify wire connections

#### No Readings
**Symptoms**: Always returns 0 or None
**Causes**:
- Broken connections
- Wrong pin assignments
- HX711 not powered
- Load cell damage

**Solutions**:
- Check all connections with multimeter
- Verify GPIO pin assignments
- Test HX711 power supply
- Replace load cell if necessary

## Food Dispensing Calibration

### Understanding Servo Control

The servo motor controls food dispensing by:
- Rotating to open/close food gate
- Controlling dispensing time
- Providing consistent portions

### Calibration Process

#### Step 1: Servo Testing

1. **Test Servo Movement**
   ```python
   from feeder_controller import FeederController
   
   controller = FeederController(servo_pin=18)
   controller.test_servo()
   ```

2. **Verify Range of Motion**
   - Servo should move 0° to 180°
   - Movement should be smooth
   - No binding or stalling

#### Step 2: Food Gate Setup

1. **Install Food Gate**
   - Attach gate to servo arm
   - Ensure proper alignment
   - Test opening/closing

2. **Adjust Gate Position**
   - Closed position: 0°
   - Open position: 90° (adjust as needed)
   - Verify food flows properly

#### Step 3: Portion Calibration

1. **Prepare for Calibration**
   - Empty food bowl
   - Tare the scale
   - Have measuring container ready

2. **Interactive Calibration**
   ```python
   from feeder_controller import FeederCalibrator
   
   calibrator = FeederCalibrator(controller)
   calibrator.interactive_calibration()
   ```

3. **Manual Calibration**
   ```python
   # Dispense for known time
   dispense_time = 2.0  # seconds
   controller.dispense_food_manual(dispense_time)
   
   # Measure dispensed amount
   dispensed_weight = 50  # grams
   
   # Calculate rate
   rate = dispensed_weight / dispense_time
   print(f"Dispensing rate: {rate} g/s")
   ```

#### Step 4: Portion Testing

1. **Test Different Portions**
   ```python
   test_portions = [25, 50, 75, 100]  # grams
   calibrator.test_dispensing(test_portions)
   ```

2. **Verify Accuracy**
   - Test multiple times for each portion
   - Calculate average and standard deviation
   - Aim for ±5% accuracy

### Calibration Parameters

#### Servo Settings
- **Min Angle**: 0° (closed)
- **Max Angle**: 180° (fully open)
- **Feeding Angle**: 90° (adjust for optimal flow)

#### Dispensing Rate
- **Typical Rate**: 10-15 g/s
- **Factors**: Food type, hopper design, gate opening
- **Adjustment**: Modify dispensing time or gate opening

### Troubleshooting Food Dispensing

#### Servo Not Moving
**Symptoms**: Servo doesn't respond
**Causes**:
- No power to servo
- Wrong signal wire
- Servo damaged
- Incorrect pin assignment

**Solutions**:
- Check servo power supply
- Verify signal wire connection
- Test servo with servo tester
- Check GPIO pin assignment

#### Inconsistent Portions
**Symptoms**: Portions vary significantly
**Causes**:
- Food bridging in hopper
- Inconsistent food flow
- Servo positioning issues
- Timing variations

**Solutions**:
- Add food agitator
- Improve hopper design
- Calibrate servo positions
- Increase dispensing time

#### Food Not Flowing
**Symptoms**: No food dispensed
**Causes**:
- Gate not opening enough
- Food stuck in hopper
- Wrong food type
- Hopper empty

**Solutions**:
- Increase gate opening angle
- Add food agitator
- Use appropriate food type
- Check food level

## Advanced Calibration

### Temperature Compensation

1. **Monitor Temperature**
   ```python
   # Add temperature sensor
   # Adjust calibration based on temperature
   ```

2. **Temperature Calibration**
   - Calibrate at different temperatures
   - Create temperature compensation table
   - Apply compensation in software

### Multiple Food Types

1. **Food Type Calibration**
   - Calibrate for each food type
   - Store calibration factors
   - Select appropriate calibration

2. **Automatic Detection**
   - Use weight sensor to detect food type
   - Adjust dispensing parameters
   - Maintain separate calibrations

### Long-term Stability

1. **Regular Verification**
   - Test calibration monthly
   - Document drift over time
   - Adjust as needed

2. **Environmental Factors**
   - Monitor humidity
   - Check for mechanical wear
   - Update calibration factors

## Calibration Data Management

### Storing Calibration Data

```python
# Save calibration data
calibration_data = {
    'weight_calibration_factor': sensor.calibration_factor,
    'weight_tare_value': sensor.tare_value,
    'servo_feeding_angle': controller.feeding_angle,
    'dispensing_rate': controller.portion_grams_per_second,
    'calibration_date': datetime.now().isoformat(),
    'calibration_weights': test_weights
}

# Save to file
with open('calibration.json', 'w') as f:
    json.dump(calibration_data, f, indent=2)
```

### Loading Calibration Data

```python
# Load calibration data
with open('calibration.json', 'r') as f:
    calibration_data = json.load(f)

# Apply calibration
sensor.set_calibration_data(
    calibration_data['weight_calibration_factor'],
    calibration_data['weight_tare_value']
)
controller.update_config({
    'feeding_angle': calibration_data['servo_feeding_angle'],
    'portion_grams_per_second': calibration_data['dispensing_rate']
})
```

## Maintenance Schedule

### Daily
- Check weight readings for stability
- Verify food dispensing accuracy
- Clean food hopper and bowl

### Weekly
- Test calibration with known weights
- Verify portion accuracy
- Check for mechanical wear

### Monthly
- Full calibration verification
- Update calibration factors if needed
- Document performance metrics

### Quarterly
- Complete recalibration
- Check all mechanical components
- Update software if needed

## Best Practices

### Calibration Environment
- Stable temperature (20-25°C)
- Minimal vibration
- Clean, dry environment
- Proper lighting for visibility

### Calibration Weights
- Use certified weights when possible
- Verify weights regularly
- Use appropriate weight range
- Handle weights carefully

### Documentation
- Record all calibration data
- Document environmental conditions
- Note any issues or adjustments
- Keep calibration history

### Validation
- Test across full weight range
- Verify multiple times
- Check for consistency
- Document results 