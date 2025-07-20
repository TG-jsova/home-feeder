# Assembly Guide - Automated Cat Feeder

## Overview

This guide will walk you through assembling the automated cat feeder from start to finish. The assembly is divided into several phases to make it manageable and ensure everything works correctly.

## Prerequisites

- All required components (see `hardware/component_list.md`)
- 3D printed parts (see `3d_models/` directory)
- Basic tools: screwdriver, wire strippers, soldering iron (optional)
- Raspberry Pi with SD card and operating system installed

## Phase 1: Electronics Assembly

### Step 1: Prepare Raspberry Pi

1. **Install Raspberry Pi OS**
   - Download Raspberry Pi Imager
   - Flash Raspberry Pi OS Lite to SD card
   - Enable SSH and WiFi during setup

2. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Required Software**
   ```bash
   sudo apt install python3-pip git -y
   cd ~
   git clone <your-repo-url>
   cd automated-cat-feeder/software
   pip3 install -r requirements.txt
   ```

### Step 2: Breadboard Setup

1. **Power Distribution**
   - Connect 5V rail to Pi Pin 2 (5V)
   - Connect GND rail to Pi Pin 6 (Ground)
   - Verify continuity with multimeter

2. **HX711 Connection**
   - VCC → 5V rail
   - GND → GND rail
   - DOUT → Pi Pin 29 (GPIO 5)
   - SCK → Pi Pin 31 (GPIO 6)

3. **Load Cell Connection**
   - Red → HX711 VCC
   - Black → HX711 GND
   - White → HX711 A+
   - Green → HX711 A-

### Step 3: Servo Motor Setup

1. **Power Supply**
   - Connect 12V power supply to voltage regulator
   - Set output to 6V for servo
   - Connect servo red wire to 6V
   - Connect servo black wire to GND

2. **Signal Connection**
   - Connect servo yellow/orange wire to Pi Pin 12 (GPIO 18)
   - Ensure common ground between Pi and servo power

### Step 4: LCD Display

1. **I2C Connection**
   - VCC → 5V rail
   - GND → GND rail
   - SDA → Pi Pin 3 (GPIO 2)
   - SCL → Pi Pin 5 (GPIO 3)

2. **Enable I2C**
   ```bash
   sudo raspi-config
   # Navigate to Interface Options → I2C → Enable
   ```

### Step 5: Push Buttons

1. **Button Connections** (with 10kΩ pull-up resistors)
   - Button 1 (Manual Feed) → Pi Pin 7 (GPIO 4)
   - Button 2 (Tare) → Pi Pin 11 (GPIO 17)
   - Button 3 (Emergency Stop) → Pi Pin 13 (GPIO 27)
   - Button 4 (Menu) → Pi Pin 15 (GPIO 22)

2. **Pull-up Resistors**
   - Connect 10kΩ resistor from each button to 5V rail
   - Connect other button terminal to GND

### Step 6: Status Indicators

1. **LED Connection**
   - Anode (+) → 220Ω resistor → Pi Pin 16 (GPIO 23)
   - Cathode (-) → GND

2. **Buzzer Connection**
   - Positive (+) → Pi Pin 18 (GPIO 24)
   - Negative (-) → GND

## Phase 2: Mechanical Assembly

### Step 1: 3D Printed Parts Preparation

1. **Print Settings**
   - Layer height: 0.2mm
   - Infill: 20-30%
   - Support: Yes (for overhangs)
   - Material: PLA or PETG

2. **Required Parts**
   - `feeder_base.stl` - Main enclosure
   - `food_hopper.stl` - Food storage container
   - `load_cell_mount.stl` - Weight sensor mount
   - `servo_mount.stl` - Servo motor bracket

### Step 2: Base Enclosure Assembly

1. **Raspberry Pi Mounting**
   - Place Pi in designated area
   - Secure with M2.5 screws and standoffs
   - Route cables through designated holes

2. **Component Mounting**
   - Mount LCD display in front panel
   - Install push buttons in button panel
   - Secure LED and buzzer in status panel

3. **Cable Management**
   - Route all cables neatly
   - Use cable ties to secure
   - Leave slack for component movement

### Step 3: Load Cell Assembly

1. **Load Cell Mounting**
   - Secure load cell to mounting bracket
   - Use M3 screws and nuts
   - Ensure proper alignment

2. **Bowl Support**
   - Place food bowl in support ring
   - Verify bowl sits level
   - Test weight measurement

### Step 4: Mason Jar Adapter Assembly

1. **Adapter Installation**
   - Attach mason jar adapter to main enclosure
   - Secure with mounting screws (4 corners)
   - Verify adapter is level and centered

2. **Servo Installation**
   - Mount servo in designated bracket on adapter
   - Connect servo arm to food gate
   - Test servo movement range

3. **Food Gate**
   - Install food gate in outlet
   - Connect to servo arm
   - Test opening/closing mechanism

4. **Mason Jar Setup**
   - Clean and dry mason jar thoroughly
   - Fill with cat food (1-2L capacity)
   - Screw jar into adapter threads
   - Verify jar is secure and level

## Phase 3: Software Setup

### Step 1: Initial Configuration

1. **Clone Repository**
   ```bash
   cd ~
   git clone <your-repo-url>
   cd automated-cat-feeder/software
   ```

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create Configuration**
   ```bash
   python3 main.py
   # This will create default config.json
   ```

### Step 2: Calibration

1. **Weight Sensor Calibration**
   ```bash
   cd ~/automated-cat-feeder/software
   python3 -c "
   from weight_sensor import WeightSensor, WeightCalibrator
   sensor = WeightSensor(5, 6)
   calibrator = WeightCalibrator(sensor)
   calibrator.interactive_calibration()
   "
   ```

2. **Feeder Calibration**
   ```bash
   python3 -c "
   from feeder_controller import FeederController, FeederCalibrator
   controller = FeederController(18)
   calibrator = FeederCalibrator(controller)
   calibrator.interactive_calibration()
   "
   ```

### Step 3: Testing

1. **Component Testing**
   ```bash
   # Test weight sensor
   python3 -c "
   from weight_sensor import WeightSensor
   sensor = WeightSensor(5, 6)
   print(f'Weight: {sensor.get_weight()}kg')
   "

   # Test servo
   python3 -c "
   from feeder_controller import FeederController
   controller = FeederController(18)
   controller.test_servo()
   "
   ```

2. **Integration Testing**
   ```bash
   # Run full system test
   python3 main.py
   ```

## Phase 4: Final Assembly

### Step 1: Enclosure Assembly

1. **Mount Base to Wall/Surface**
   - Use provided mounting brackets
   - Ensure level installation
   - Secure with appropriate screws

2. **Attach Load Cell Mount**
   - Connect to main enclosure
   - Route cables through strain relief
   - Test weight measurement

3. **Install Food Hopper**
   - Attach to main enclosure
   - Connect servo cables
   - Test food dispensing

### Step 2: Final Testing

1. **System Test**
   ```bash
   python3 main.py
   ```

2. **Web Interface**
   - Open browser to `http://raspberry-pi-ip:5000`
   - Test all functions
   - Verify data logging

3. **Manual Controls**
   - Test all push buttons
   - Verify emergency stop
   - Check status indicators

### Step 3: Calibration Verification

1. **Weight Accuracy**
   - Test with known weights
   - Verify readings are consistent
   - Adjust calibration if needed

2. **Food Portion Accuracy**
   - Test different portion sizes
   - Measure actual dispensed amounts
   - Adjust dispensing rate if needed

## Troubleshooting

### Common Issues

**Weight Sensor Not Working:**
- Check wire connections
- Verify HX711 power
- Test with multimeter

**Servo Not Moving:**
- Check power supply voltage
- Verify signal wire connection
- Test with servo tester

**LCD Not Displaying:**
- Check I2C address
- Verify power connections
- Test with I2C scanner

**Buttons Not Responding:**
- Check pull-up resistors
- Verify GPIO pin assignments
- Test with simple script

### Debug Commands

```bash
# Check GPIO status
gpio readall

# Test I2C devices
i2cdetect -y 1

# Check system logs
tail -f cat_feeder.log

# Test weight sensor
python3 -c "from weight_sensor import WeightSensor; s = WeightSensor(5, 6); print(s.get_weight())"
```

## Safety Considerations

### Electrical Safety
- Double-check all connections before powering on
- Use appropriate wire gauges
- Ensure proper grounding
- Protect against moisture

### Mechanical Safety
- Secure all moving parts
- Prevent pinch points
- Use food-safe materials
- Ensure stability

### Pet Safety
- No exposed wires
- No sharp edges
- Secure mounting
- Non-toxic materials

## Maintenance

### Regular Maintenance
- Clean food hopper weekly
- Check weight sensor accuracy monthly
- Update software as needed
- Backup configuration and data

### Calibration Schedule
- Weight sensor: Monthly
- Food dispensing: Weekly
- Full system: Quarterly

## Next Steps

1. **Customization**: Modify feeding schedules and portions
2. **Monitoring**: Set up remote monitoring and alerts
3. **Expansion**: Add camera module for monitoring
4. **Integration**: Connect to smart home systems

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code documentation
- Create an issue on the project repository
- Consult the community forums 