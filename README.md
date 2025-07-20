# Automated Cat Feeder with Weight Sensing

An intelligent cat feeder that dispenses food based on weight measurements using a Raspberry Pi 4, load cell sensor, and servo motor.

## Features

- **Weight-based feeding**: Dispenses food based on cat's weight
- **Scheduled feeding**: Set multiple feeding times per day
- **Portion control**: Adjustable portion sizes
- **Web interface**: Control and monitor via web browser
- **Data logging**: Track feeding history and weight trends
- **3D printed enclosure**: Custom designed housing

## Hardware Components

### Required Components
- Raspberry Pi 4 (4GB or 8GB recommended)
- Load Cell (5kg capacity) with HX711 amplifier
- SG90 or MG996R servo motor
- 16x2 LCD display with I2C interface
- 4x push buttons for manual control
- 5V power supply for Raspberry Pi
- 12V power supply for servo motor
- Breadboard and jumper wires
- 3D printed enclosure parts

### Optional Components
- Camera module for monitoring
- LED strip for status indication
- Buzzer for alerts
- Real-time clock module (DS3231)

## Project Structure

```
automated-cat-feeder/
├── software/
│   ├── main.py                 # Main application
│   ├── feeder_controller.py    # Hardware control
│   ├── weight_sensor.py        # Load cell interface
│   ├── web_interface.py        # Flask web server
│   ├── database.py             # SQLite database
│   └── requirements.txt        # Python dependencies
├── hardware/
│   ├── wiring_diagram.png      # Circuit diagram
│   ├── wiring_diagram.fzz      # Fritzing file
│   └── component_list.md       # Detailed parts list
├── 3d_models/
│   ├── feeder_base.stl         # Main enclosure
│   ├── food_hopper.stl         # Food storage container
│   ├── servo_mount.stl         # Servo motor bracket
│   ├── load_cell_mount.stl     # Weight sensor mount
│   └── display_mount.stl       # LCD display holder
├── docs/
│   ├── assembly_guide.md       # Step-by-step assembly
│   ├── calibration_guide.md    # Weight sensor calibration
│   └── troubleshooting.md      # Common issues and solutions
└── README.md                   # This file
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd automated-cat-feeder
   ```

2. **Install dependencies**
   ```bash
   cd software
   pip install -r requirements.txt
   ```

3. **Assemble hardware** (see `docs/assembly_guide.md`)

4. **Calibrate weight sensor** (see `docs/calibration_guide.md`)

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access web interface** at `http://raspberry-pi-ip:5000`

## Configuration

The system can be configured through the web interface or by editing `config.json`:

- Feeding schedules
- Portion sizes
- Weight thresholds
- Calibration settings

## Safety Features

- Emergency stop button
- Weight limit protection
- Servo motor current monitoring
- Food level detection
- Error logging and alerts

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines. 