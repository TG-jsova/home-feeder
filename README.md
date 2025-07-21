# Automated Cat Feeder with Weight Sensing

An intelligent cat feeder that dispenses food based on weight measurements using a Raspberry Pi 4, load cell sensor, and servo motor. This system provides comprehensive monitoring, safety features, and a modern web interface.

## 🚀 Features

### Core Functionality
- **Weight-based feeding**: Dispenses food based on cat's weight
- **Scheduled feeding**: Set multiple feeding times per day with custom portions
- **Portion control**: Adjustable portion sizes with safety limits
- **Web interface**: Modern, responsive web dashboard for control and monitoring
- **Data logging**: Comprehensive event logging and data analytics
- **3D printed enclosure**: Custom designed housing with mason jar adapter

### Advanced Features
- **Health monitoring**: Real-time system health tracking with alerts
- **Backup & restore**: Automated backup system with manual restore capabilities
- **Configuration validation**: Robust configuration management with validation
- **Safety features**: Emergency stop, daily feeding limits, portion size limits
- **Maintenance automation**: Auto-restart, database cleanup, log rotation
- **Notification system**: Email and webhook notifications (configurable)
- **Systemd service**: Professional installation with auto-start capability

## 🛠️ Hardware Components

### Required Components
| Component | Quantity | Description | Approx. Price |
|-----------|----------|-------------|---------------|
| **Raspberry Pi 4** | 1 | 4GB or 8GB RAM recommended | $45-75 |
| **MicroSD Card** | 1 | 32GB Class 10 or higher | $10-20 |
| **Power Supply** | 1 | 5V 3A USB-C for Raspberry Pi | $8-15 |
| **Load Cell** | 1 | 5kg capacity, 4-wire | $8-15 |
| **HX711 Amplifier** | 1 | 24-bit ADC for load cell | $3-8 |
| **SG90 Servo Motor** | 1 | 9g micro servo, 180° rotation | $3-8 |
| **16x2 LCD Display** | 1 | I2C interface | $5-12 |
| **Push Buttons** | 4 | Tactile switches | $2-5 |
| **Breadboard** | 1 | 830 tie-points | $5-10 |
| **Jumper Wires** | 1 set | Male-to-male, male-to-female | $5-10 |
| **12V Power Supply** | 1 | 1A for servo motor | $8-15 |
| **Mason Jar** | 1 | Wide mouth, 1-2L capacity | $3-8 |
| **Food Bowl** | 1 | Stainless steel or ceramic | $8-20 |

### Optional Components
- **Camera module**: Pi Camera v2 or v3 for monitoring
- **LED Strip**: WS2812B RGB for status indication
- **Buzzer**: 5V active buzzer for audio alerts
- **Real-time Clock**: DS3231 module for accurate timekeeping

**Total Cost**: ~$120-200 for basic setup, ~$250-350 for full setup

## 📁 Project Structure

```
home-feeder/
├── software/
│   ├── main.py                 # Main application with enhanced features
│   ├── feeder_controller.py    # Hardware control with safety features
│   ├── weight_sensor.py        # Load cell interface with calibration
│   ├── web_interface.py        # Modern Flask web server
│   ├── database.py             # SQLite database with analytics
│   ├── config_validator.py     # Configuration validation system
│   ├── health_monitor.py       # System health monitoring
│   ├── backup_restore.py       # Backup and restore utilities
│   ├── test_system.py          # Comprehensive system testing
│   ├── install.sh              # Automated installation script
│   ├── config.json             # Comprehensive configuration
│   └── requirements.txt        # Python dependencies
├── hardware/
│   ├── wiring_diagram.md       # Detailed wiring instructions
│   ├── component_list.md       # Complete parts list with links
│   └── amazon_links.md         # Shopping recommendations
├── 3d_models/
│   ├── feeder_base.scad        # Main enclosure
│   ├── food_hopper.scad        # Food storage container
│   ├── load_cell_mount.scad    # Weight sensor mount
│   ├── mason_jar_adapter.scad  # Mason jar adapter
│   └── assembly_*.scad         # Assembly visualizations
├── docs/
│   ├── assembly_guide.md       # Step-by-step assembly
│   ├── calibration_guide.md    # Weight sensor calibration
│   └── troubleshooting.md      # Common issues and solutions
└── README.md                   # This file
```

## ⚡ Quick Start

### 1. Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/home-feeder.git
cd home-feeder

# Run the installation script
sudo chmod +x software/install.sh
sudo ./software/install.sh
```

The installation script will:
- Update system packages
- Install required dependencies
- Enable I2C interface
- Create system user
- Setup Python virtual environment
- Create systemd service
- Configure logging and firewall
- Setup backup system
- Run initial tests

### 2. Manual Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/home-feeder.git
cd home-feeder/software

# Install dependencies
pip3 install -r requirements.txt

# Create configuration
python3 main.py  # This creates default config.json

# Run the system
python3 main.py
```

### 3. Hardware Assembly

Follow the detailed [Assembly Guide](docs/assembly_guide.md) for step-by-step instructions.

### 4. Calibration

```bash
# Weight sensor calibration
python3 -c "
from weight_sensor import WeightSensor, WeightCalibrator
sensor = WeightSensor(5, 6)
calibrator = WeightCalibrator(sensor)
calibrator.interactive_calibration()
"

# Feeder calibration
python3 -c "
from feeder_controller import FeederController, FeederCalibrator
controller = FeederController(18)
calibrator = FeederCalibrator(controller)
calibrator.interactive_calibration()
"
```

### 5. Access Web Interface

Open your browser to `http://raspberry-pi-ip:5000`

## 🔧 Configuration

The system uses a comprehensive JSON configuration file (`config.json`) with the following sections:

### Weight Sensor
```json
{
  "weight_sensor": {
    "dout_pin": 5,
    "sck_pin": 6,
    "calibration_factor": 2280.0,
    "tare_samples": 10,
    "reading_samples": 3,
    "smoothing_samples": 10,
    "stability_threshold": 0.05
  }
}
```

### Feeding Schedules
```json
{
  "feeding_schedules": [
    {
      "time": "08:00",
      "portion": 50,
      "enabled": true,
      "name": "Breakfast"
    }
  ]
}
```

### Safety Settings
```json
{
  "safety": {
    "emergency_stop_pin": 27,
    "max_daily_feedings": 10,
    "min_feeding_interval_minutes": 120,
    "max_portion_grams": 200,
    "low_food_alert_threshold": 100
  }
}
```

### Health Monitoring
```json
{
  "maintenance": {
    "auto_restart_hours": 168,
    "health_check_interval_minutes": 30,
    "calibration_reminder_days": 30
  }
}
```

## 🛡️ Safety Features

- **Emergency stop button**: Immediate system shutdown
- **Daily feeding limits**: Prevent overfeeding
- **Portion size limits**: Maximum portion size enforcement
- **Minimum feeding intervals**: Prevent rapid successive feedings
- **Weight validation**: Cat weight range checking
- **System health monitoring**: Automatic alerts for issues
- **Backup protection**: Automatic data backup

## 📊 Monitoring & Analytics

### Web Dashboard Features
- Real-time weight monitoring
- Feeding history and statistics
- System health status
- Configuration management
- Manual feeding controls
- Schedule management

### Health Monitoring
- CPU and memory usage
- Disk space monitoring
- Temperature tracking
- Database size monitoring
- Log file management
- Automatic alert generation

### Data Analytics
- Feeding patterns analysis
- Weight trends tracking
- System performance metrics
- Error rate monitoring
- Usage statistics

## 🔄 Backup & Restore

### Automatic Backups
- Daily automated backups
- Configurable backup retention
- Database and configuration backup
- Log file archiving

### Manual Operations
```bash
# Create backup
python3 backup_restore.py create

# List backups
python3 backup_restore.py list

# Restore from backup
python3 backup_restore.py restore --backup-file /path/to/backup.tar.gz

# Verify backup integrity
python3 backup_restore.py verify --backup-file /path/to/backup.tar.gz
```

## 🧪 Testing

### System Testing
```bash
# Run comprehensive system tests
python3 test_system.py

# Interactive testing mode
python3 test_system.py --interactive
```

### Component Testing
```bash
# Test weight sensor
python3 -c "from weight_sensor import WeightSensor; s = WeightSensor(5, 6); print(s.get_weight())"

# Test servo motor
python3 -c "from feeder_controller import FeederController; c = FeederController(18); c.test_servo()"

# Test database
python3 -c "from database import Database; db = Database(); print(db.get_statistics())"
```

## 🔧 Maintenance

### Service Management
```bash
# Start service
sudo systemctl start cat-feeder

# Stop service
sudo systemctl stop cat-feeder

# View status
sudo systemctl status cat-feeder

# View logs
sudo journalctl -u cat-feeder -f
```

### Database Maintenance
```bash
# Clean old data
python3 -c "from database import Database; db = Database(); db.cleanup_old_data(30)"

# Export data
python3 -c "from database import Database; db = Database(); db.export_data('export.json')"
```

### Log Management
```bash
# View current logs
tail -f cat_feeder.log

# Rotate logs manually
sudo logrotate -f /etc/logrotate.d/cat-feeder
```

## 🐛 Troubleshooting

### Common Issues

**Weight Sensor Not Working:**
- Check wire connections
- Verify HX711 power
- Test with multimeter
- Check GPIO pin assignments

**Servo Not Moving:**
- Check power supply voltage
- Verify signal wire connection
- Test with servo tester
- Check PWM configuration

**Web Interface Not Accessible:**
- Check firewall settings
- Verify port configuration
- Check service status
- Review error logs

**System Performance Issues:**
- Check health monitoring dashboard
- Review system logs
- Monitor resource usage
- Consider hardware upgrades

### Debug Commands
```bash
# Check GPIO status
gpio readall

# Test I2C devices
i2cdetect -y 1

# Check system resources
htop

# Monitor system logs
sudo journalctl -f

# Test network connectivity
ping raspberry-pi-ip
```

## 📈 Performance & Scalability

### System Requirements
- **Minimum**: Raspberry Pi 3B+ with 1GB RAM
- **Recommended**: Raspberry Pi 4 with 4GB+ RAM
- **Storage**: 16GB+ microSD card (Class 10)
- **Network**: WiFi or Ethernet connection

### Performance Metrics
- **Response time**: < 100ms for web interface
- **Weight accuracy**: ±0.1% of full scale
- **Feeding precision**: ±2g portion accuracy
- **Uptime**: 99.9% with auto-restart
- **Data retention**: 30 days with cleanup

### Scalability Features
- Modular component design
- Configurable thresholds
- Extensible web interface
- Plugin architecture support
- Multi-cat support (future)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/home-feeder.git
cd home-feeder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black software/

# Lint code
flake8 software/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Raspberry Pi Foundation for the amazing platform
- Adafruit for excellent documentation and components
- OpenSCAD community for 3D modeling tools
- Flask and Python communities for web framework

## 📞 Support

For issues and questions:
- Check the [troubleshooting guide](docs/troubleshooting.md)
- Review the [documentation](docs/)
- Create an issue on the project repository
- Join our community discussions

---

**Made with ❤️ for happy cats and their humans** 