# Hardware Component List

## Required Components

### Core Components

| Component | Quantity | Description | Approx. Price | Notes |
|-----------|----------|-------------|---------------|-------|
| **Raspberry Pi 4** | 1 | 4GB or 8GB RAM recommended | $45-75 | Main controller |
| **MicroSD Card** | 1 | 32GB Class 10 or higher | $10-20 | Operating system storage |
| **Power Supply** | 1 | 5V 3A USB-C for Raspberry Pi | $8-15 | Official Pi supply recommended |

### Sensors & Actuators

| Component | Quantity | Description | Approx. Price | Notes |
|-----------|----------|-------------|---------------|-------|
| **Load Cell** | 1 | 5kg capacity, 4-wire | $8-15 | Weight measurement |
| **HX711 Amplifier** | 1 | 24-bit ADC for load cell | $3-8 | Converts analog to digital |
| **SG90 Servo Motor** | 1 | 9g micro servo, 180° rotation | $3-8 | Food dispensing mechanism |
| **16x2 LCD Display** | 1 | I2C interface | $5-12 | Status display |
| **Push Buttons** | 4 | Tactile switches | $2-5 | Manual control |

### Power & Wiring

| Component | Quantity | Description | Approx. Price | Notes |
|-----------|----------|-------------|---------------|-------|
| **Breadboard** | 1 | 830 tie-points | $5-10 | Prototyping |
| **Jumper Wires** | 1 set | Male-to-male, male-to-female | $5-10 | Connections |
| **GPIO Extension Cable** | 1 | 40-pin ribbon cable | $3-8 | Pi to breadboard |
| **12V Power Supply** | 1 | 1A for servo motor | $8-15 | Servo power |

### Enclosure & Mechanical

| Component | Quantity | Description | Approx. Price | Notes |
|-----------|----------|-------------|---------------|-------|
| **3D Printed Parts** | 1 set | Custom designed enclosure | $15-30 | See 3D models |
| **Mason Jar** | 1 | Wide mouth, 1-2L capacity | $3-8 | Food storage (reusable) |
| **Mason Jar Adapter** | 1 | 3D printed threaded adapter | $5-10 | Connects jar to feeder |
| **Food Bowl** | 1 | Stainless steel or ceramic | $8-20 | Cat feeding bowl |
| **Mounting Hardware** | 1 set | Screws, nuts, washers | $5-10 | Assembly |

## Optional Components

| Component | Quantity | Description | Approx. Price | Notes |
|-----------|----------|-------------|---------------|-------|
| **Camera Module** | 1 | Pi Camera v2 or v3 | $25-50 | Monitoring |
| **LED Strip** | 1 | WS2812B RGB | $8-15 | Status indication |
| **Buzzer** | 1 | 5V active buzzer | $2-5 | Audio alerts |
| **Real-time Clock** | 1 | DS3231 module | $3-8 | Accurate timekeeping |
| **WiFi Dongle** | 1 | USB WiFi adapter | $8-15 | If Pi doesn't have WiFi |

## Recommended Suppliers

### Primary Sources
- **Adafruit** - High-quality components, good documentation
- **SparkFun** - Reliable parts, excellent tutorials
- **Amazon** - Wide selection, fast shipping
- **AliExpress** - Budget option, longer shipping

### Specific Product Links

For detailed Amazon links and shopping recommendations, see [amazon_links.md](amazon_links.md).

#### Key Components Search Terms
- **Load Cell**: Search "5kg load cell HX711 weight sensor"
- **Servo**: Search "SG90 micro servo 5 pack"
- **LCD Display**: Search "16x2 LCD I2C display Arduino"
- **Mason Jars**: Search "wide mouth mason jars 32oz 12 pack"
- **Raspberry Pi**: Search "Raspberry Pi 4 4GB"
- **Power Supply**: Search "Raspberry Pi 4 power supply official"

## Total Cost Estimate

### Basic Setup (Required Components)
- **Minimum**: ~$120-150
- **Recommended**: ~$180-220

### Full Setup (Including Optional Components)
- **Complete**: ~$250-350

## Component Specifications

### Load Cell
- **Capacity**: 5kg (11 lbs)
- **Accuracy**: ±0.1% of full scale
- **Output**: 2mV/V typical
- **Excitation**: 5-10V DC
- **Operating Temperature**: -10°C to +50°C

### HX711 Amplifier
- **Resolution**: 24-bit ADC
- **Sample Rate**: 10 or 80 samples per second
- **Input Voltage**: 2.6-5.5V
- **Operating Current**: <1.5mA
- **Interface**: Serial communication

### SG90 Servo
- **Operating Voltage**: 4.8-6V
- **Torque**: 1.8kg/cm at 4.8V
- **Speed**: 0.1s/60° at 4.8V
- **Rotation**: 180°
- **Weight**: 9g
- **Dimensions**: 22.2 x 11.8 x 31mm

### LCD Display
- **Display**: 16x2 characters
- **Interface**: I2C
- **Voltage**: 3.3-5V
- **Backlight**: Blue/White
- **Contrast**: Adjustable

## Alternative Components

### Load Cell Alternatives
- **10kg Load Cell**: For larger cats or multiple cats
- **20kg Load Cell**: For very large cats
- **Strain Gauge**: More precise but complex

### Servo Alternatives
- **Stepper Motor**: More precise control, higher cost
- **DC Motor with Encoder**: Continuous rotation, more complex
- **Solenoid Valve**: For liquid dispensing

### Display Alternatives
- **OLED Display**: Better visibility, higher cost
- **E-Paper Display**: Low power, good visibility
- **Touch Screen**: Interactive interface, higher cost

## Quality Considerations

### High-Quality Options
- **Load Cell**: Use industrial-grade for better accuracy
- **Servo**: Metal gear servos for durability
- **Power Supply**: Official Pi supply for reliability

### Budget Options
- **Load Cell**: Generic 5kg load cell
- **Servo**: Plastic gear SG90
- **Display**: Basic 16x2 LCD without I2C

## Safety Considerations

### Electrical Safety
- Use appropriate power supplies
- Ensure proper grounding
- Protect against moisture
- Use fuses for protection

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