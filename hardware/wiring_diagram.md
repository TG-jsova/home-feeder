# Wiring Diagram for Automated Cat Feeder

## Pin Assignments

### Raspberry Pi 4 GPIO Pins

| Component | Pi Pin | BCM | Function | Notes |
|-----------|--------|-----|----------|-------|
| **HX711 DOUT** | 29 | GPIO 5 | Data Input | Load cell data |
| **HX711 SCK** | 31 | GPIO 6 | Clock Output | Load cell clock |
| **Servo Signal** | 12 | GPIO 18 | PWM Output | Servo control |
| **LCD SDA** | 3 | GPIO 2 | I2C Data | LCD communication |
| **LCD SCL** | 5 | GPIO 3 | I2C Clock | LCD communication |
| **Button 1** | 7 | GPIO 4 | Input | Manual feed |
| **Button 2** | 11 | GPIO 17 | Input | Tare scale |
| **Button 3** | 13 | GPIO 27 | Input | Emergency stop |
| **Button 4** | 15 | GPIO 22 | Input | Menu navigation |
| **LED Status** | 16 | GPIO 23 | Output | Status indicator |
| **Buzzer** | 18 | GPIO 24 | Output | Audio alerts |

### Power Connections

| Component | Voltage | Source | Notes |
|-----------|---------|--------|-------|
| **Raspberry Pi** | 5V | USB-C Power Supply | Main power |
| **HX711** | 5V | Pi 5V Pin | Sensor power |
| **LCD Display** | 5V | Pi 5V Pin | Display power |
| **Servo Motor** | 6V | External 12V Supply | Motor power |
| **Load Cell** | 5V | Pi 5V Pin | Excitation voltage |

## Detailed Wiring Instructions

### 1. Load Cell & HX711 Connection

```
Load Cell (4-wire) → HX711 → Raspberry Pi
```

**Load Cell to HX711:**
- Red wire → VCC (5V)
- Black wire → GND
- White wire → A+
- Green wire → A-

**HX711 to Raspberry Pi:**
- VCC → Pi Pin 2 (5V)
- GND → Pi Pin 6 (Ground)
- DOUT → Pi Pin 29 (GPIO 5)
- SCK → Pi Pin 31 (GPIO 6)

### 2. Servo Motor Connection

```
Servo Motor → External Power Supply + Raspberry Pi
```

**Servo to Power Supply:**
- Red wire → 6V (from 12V supply with voltage regulator)
- Black wire → GND

**Servo to Raspberry Pi:**
- Yellow/Orange wire → Pi Pin 12 (GPIO 18)

**Power Supply:**
- 12V input → 6V output (use voltage regulator)
- GND → Common ground with Pi

### 3. LCD Display Connection (I2C)

```
LCD Display → Raspberry Pi (I2C)
```

**LCD to Raspberry Pi:**
- VCC → Pi Pin 2 (5V)
- GND → Pi Pin 6 (Ground)
- SDA → Pi Pin 3 (GPIO 2)
- SCL → Pi Pin 5 (GPIO 3)

### 4. Push Buttons Connection

```
Push Buttons → Raspberry Pi (with pull-up resistors)
```

**Button 1 (Manual Feed):**
- One terminal → Pi Pin 7 (GPIO 4)
- Other terminal → Pi Pin 6 (Ground)
- 10kΩ pull-up resistor → Pi Pin 2 (5V)

**Button 2 (Tare Scale):**
- One terminal → Pi Pin 11 (GPIO 17)
- Other terminal → Pi Pin 6 (Ground)
- 10kΩ pull-up resistor → Pi Pin 2 (5V)

**Button 3 (Emergency Stop):**
- One terminal → Pi Pin 13 (GPIO 27)
- Other terminal → Pi Pin 6 (Ground)
- 10kΩ pull-up resistor → Pi Pin 2 (5V)

**Button 4 (Menu):**
- One terminal → Pi Pin 15 (GPIO 22)
- Other terminal → Pi Pin 6 (Ground)
- 10kΩ pull-up resistor → Pi Pin 2 (5V)

### 5. Status LED Connection

```
LED → Raspberry Pi (with current limiting resistor)
```

**LED to Raspberry Pi:**
- Anode (+) → 220Ω resistor → Pi Pin 16 (GPIO 23)
- Cathode (-) → Pi Pin 6 (Ground)

### 6. Buzzer Connection

```
Buzzer → Raspberry Pi
```

**Buzzer to Raspberry Pi:**
- Positive (+) → Pi Pin 18 (GPIO 24)
- Negative (-) → Pi Pin 6 (Ground)

## Breadboard Layout

### Power Distribution
```
5V Rail: Pi Pin 2, 4
GND Rail: Pi Pin 6, 9, 14, 20, 25, 30, 34, 39
```

### Component Placement
```
Top Row: HX711, LCD Display
Middle Row: Push Buttons, LED, Buzzer
Bottom Row: Servo Signal, Power Distribution
```

## Safety Considerations

### Electrical Safety
1. **Double-check all connections** before powering on
2. **Use appropriate wire gauges** for current requirements
3. **Ensure proper grounding** for all components
4. **Protect against short circuits** with proper insulation
5. **Use fuses** for power supply protection

### Component Protection
1. **Add flyback diodes** for inductive loads (servo)
2. **Use current limiting resistors** for LEDs
3. **Add decoupling capacitors** near sensitive components
4. **Protect against voltage spikes** with TVS diodes

### Mechanical Safety
1. **Secure all wires** to prevent strain on connections
2. **Use cable ties** to organize wiring
3. **Leave slack** for component movement
4. **Protect against moisture** with proper enclosure

## Testing Procedure

### 1. Power-Up Test
1. Connect power supply to Raspberry Pi only
2. Verify Pi boots correctly
3. Check all GPIO pins are accessible

### 2. Component Test
1. **Load Cell**: Test with known weight
2. **Servo**: Test movement through full range
3. **LCD**: Test display and backlight
4. **Buttons**: Test input detection
5. **LED**: Test brightness and control
6. **Buzzer**: Test audio output

### 3. Integration Test
1. Test weight measurement accuracy
2. Test food dispensing mechanism
3. Test button controls
4. Test display updates
5. Test emergency stop function

## Troubleshooting

### Common Issues

**Load Cell Not Reading:**
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

### Debug Tools
- **Multimeter**: Voltage and continuity testing
- **Oscilloscope**: Signal analysis
- **I2C Scanner**: LCD communication testing
- **GPIO Test Script**: Pin functionality testing

## Alternative Wiring Options

### Using GPIO Extension Board
- **Advantage**: Easier connections, labeled pins
- **Disadvantage**: Additional cost, bulk

### Using Custom PCB
- **Advantage**: Professional, compact, reliable
- **Disadvantage**: Higher cost, longer development time

### Using Arduino as Slave
- **Advantage**: Real-time control, simpler programming
- **Disadvantage**: Additional complexity, communication overhead 