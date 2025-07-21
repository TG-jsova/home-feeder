# Troubleshooting Guide

This guide covers common issues and their solutions for the Automated Cat Feeder system.

## 🔍 Quick Diagnostics

### System Status Check
```bash
# Check if service is running
sudo systemctl status cat-feeder

# Check recent logs
sudo journalctl -u cat-feeder -n 50

# Check system resources
htop

# Check disk space
df -h

# Check network connectivity
ping 8.8.8.8
```

### Hardware Diagnostics
```bash
# Check GPIO status
gpio readall

# Check I2C devices
i2cdetect -y 1

# Check USB devices
lsusb

# Check temperature
vcgencmd measure_temp
```

## 🚨 Common Issues

### 1. Service Won't Start

**Symptoms:**
- `systemctl start cat-feeder` fails
- Service shows as "failed" in status

**Solutions:**

**A. Check Python Environment**
```bash
# Verify Python installation
python3 --version

# Check virtual environment
ls -la /opt/cat-feeder/software/venv/

# Recreate virtual environment if needed
cd /opt/cat-feeder/software
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**B. Check Dependencies**
```bash
# Install missing packages
sudo apt update
sudo apt install python3-pip python3-venv git

# Check for missing Python packages
cd /opt/cat-feeder/software
source venv/bin/activate
python -c "import RPi.GPIO, hx711, flask"
```

**C. Check Permissions**
```bash
# Fix ownership
sudo chown -R catfeeder:catfeeder /opt/cat-feeder

# Fix permissions
sudo chmod +x /opt/cat-feeder/software/main.py
```

**D. Check Configuration**
```bash
# Validate configuration
cd /opt/cat-feeder/software
python3 -c "
from config_validator import validate_config_file
is_valid, config = validate_config_file('config.json')
print(f'Config valid: {is_valid}')
"
```

### 2. Weight Sensor Issues

**Symptoms:**
- Weight readings are 0 or incorrect
- "Sensor not initialized" errors
- Unstable readings

**Solutions:**

**A. Check Wiring**
```bash
# Verify GPIO connections
gpio readall | grep -E "(5|6)"

# Check voltage at HX711
# VCC should be 5V, GND should be 0V
```

**B. Test HX711 Communication**
```bash
# Simple HX711 test
python3 -c "
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)
hx = HX711(5, 6)
hx.set_reading_format('MSB', 'MSB')
hx.set_reference_unit(2280.0)
hx.reset()
hx.tare()
print('Raw reading:', hx.get_raw_data(5))
"
```

**C. Calibrate Sensor**
```bash
# Run calibration
cd /opt/cat-feeder/software
python3 -c "
from weight_sensor import WeightSensor, WeightCalibrator
sensor = WeightSensor(5, 6)
calibrator = WeightCalibrator(sensor)
calibrator.interactive_calibration()
"
```

**D. Check Load Cell**
- Verify load cell is properly mounted
- Check for loose connections
- Ensure no mechanical interference
- Test with known weight

### 3. Servo Motor Issues

**Symptoms:**
- Servo doesn't move
- Jerky or inconsistent movement
- Servo makes noise but doesn't move

**Solutions:**

**A. Check Power Supply**
```bash
# Verify servo power
# Should be 4.8-6V for SG90 servo
# Check voltage at servo connector
```

**B. Test Servo Signal**
```bash
# Test servo with simple script
python3 -c "
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

# Test different positions
for angle in [0, 90, 180, 90, 0]:
    duty = angle / 18 + 2
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)

pwm.stop()
GPIO.cleanup()
"
```

**C. Check Mechanical Assembly**
- Verify servo arm is properly attached
- Check for binding in food gate mechanism
- Ensure servo mounting is secure
- Lubricate moving parts if needed

### 4. Web Interface Issues

**Symptoms:**
- Can't access web interface
- Interface loads but doesn't respond
- JavaScript errors in browser

**Solutions:**

**A. Check Network**
```bash
# Check if port is open
netstat -tlnp | grep 5000

# Check firewall
sudo ufw status

# Allow port if needed
sudo ufw allow 5000
```

**B. Check Flask Service**
```bash
# Test Flask directly
cd /opt/cat-feeder/software
source venv/bin/activate
python3 -c "
from web_interface import WebInterface
from main import CatFeeder
feeder = CatFeeder()
web = WebInterface(feeder)
print('Web interface initialized')
"
```

**C. Check Browser**
- Clear browser cache
- Try different browser
- Check for JavaScript errors in developer console
- Disable browser extensions temporarily

### 5. Database Issues

**Symptoms:**
- Database errors in logs
- Missing feeding history
- Corrupted data

**Solutions:**

**A. Check Database File**
```bash
# Check database size and permissions
ls -la /opt/cat-feeder/software/cat_feeder.db

# Check database integrity
cd /opt/cat-feeder/software
sqlite3 cat_feeder.db "PRAGMA integrity_check;"
```

**B. Backup and Recreate**
```bash
# Create backup
cp cat_feeder.db cat_feeder.db.backup

# Recreate database
rm cat_feeder.db
python3 -c "
from database import Database
db = Database()
print('Database recreated')
"
```

**C. Restore from Backup**
```bash
# List available backups
python3 backup_restore.py list

# Restore database
python3 backup_restore.py restore --backup-file /path/to/backup.tar.gz --restore-database
```

### 6. Performance Issues

**Symptoms:**
- Slow web interface response
- High CPU usage
- System becomes unresponsive

**Solutions:**

**A. Check System Resources**
```bash
# Monitor CPU and memory
htop

# Check disk usage
df -h

# Check temperature
vcgencmd measure_temp
```

**B. Optimize Configuration**
```bash
# Reduce logging level
# Edit config.json
{
  "logging": {
    "level": "WARNING"
  }
}

# Reduce health check frequency
{
  "maintenance": {
    "health_check_interval_minutes": 60
  }
}
```

**C. Clean Up Data**
```bash
# Clean old database records
python3 -c "
from database import Database
db = Database()
db.cleanup_old_data(7)  # Keep only 7 days
"

# Rotate logs
sudo logrotate -f /etc/logrotate.d/cat-feeder
```

### 7. Power Issues

**Symptoms:**
- System shuts down unexpectedly
- Servo doesn't have enough power
- Voltage drops under load

**Solutions:**

**A. Check Power Supply**
- Use official Raspberry Pi power supply
- Ensure adequate current rating (3A+)
- Check for voltage drops under load
- Use separate power supply for servo

**B. Add Power Filtering**
```bash
# Add capacitors to power rails
# 100µF electrolytic + 0.1µF ceramic
# Place close to power input
```

**C. Monitor Power**
```bash
# Check voltage
vcgencmd measure_volts core

# Check current
vcgencmd measure_current core
```

## 🔧 Advanced Troubleshooting

### Debug Mode
```bash
# Enable debug logging
# Edit config.json
{
  "logging": {
    "level": "DEBUG"
  }
}

# Restart service
sudo systemctl restart cat-feeder

# Monitor logs
sudo journalctl -u cat-feeder -f
```

### Component Testing
```bash
# Run comprehensive tests
cd /opt/cat-feeder/software
python3 test_system.py

# Test individual components
python3 test_system.py --interactive
```

### Network Diagnostics
```bash
# Check network configuration
ip addr show

# Test connectivity
ping -c 4 8.8.8.8

# Check DNS
nslookup google.com

# Test port connectivity
telnet localhost 5000
```

### Hardware Diagnostics
```bash
# Check GPIO pins
gpio readall

# Test I2C bus
i2cdetect -y 1

# Check SPI (if used)
ls /dev/spidev*

# Monitor interrupts
cat /proc/interrupts
```

## 📞 Getting Help

### Before Asking for Help

1. **Check the logs:**
   ```bash
   sudo journalctl -u cat-feeder -n 100
   ```

2. **Run diagnostics:**
   ```bash
   python3 test_system.py
   ```

3. **Gather system info:**
   ```bash
   # System information
   uname -a
   cat /etc/os-release
   
   # Hardware information
   vcgencmd get_mem arm
   vcgencmd get_mem gpu
   
   # Network information
   ip addr show
   ```

4. **Document the issue:**
   - What were you doing when the problem occurred?
   - What error messages did you see?
   - What have you already tried?
   - What hardware are you using?

### Where to Get Help

1. **Check existing issues** on the project repository
2. **Search the documentation** for similar problems
3. **Create a new issue** with detailed information
4. **Join community discussions** for real-time help

### Information to Include

When reporting an issue, please include:

- **System details**: Raspberry Pi model, OS version
- **Hardware setup**: Components used, wiring diagram
- **Software version**: Git commit hash or version number
- **Error messages**: Complete error logs
- **Steps to reproduce**: Detailed steps to recreate the issue
- **Expected vs actual behavior**: What should happen vs what happens

## 🛠️ Preventive Maintenance

### Regular Tasks

**Daily:**
- Check system status
- Review recent logs
- Verify feeding schedules

**Weekly:**
- Clean food hopper and bowl
- Check weight sensor accuracy
- Review system health metrics

**Monthly:**
- Calibrate weight sensor
- Clean up old data
- Update system packages
- Check for software updates

**Quarterly:**
- Full system test
- Hardware inspection
- Backup verification
- Performance review

### Monitoring Setup

```bash
# Set up log monitoring
sudo journalctl -u cat-feeder -f

# Monitor system resources
htop

# Check disk space
watch -n 60 'df -h'

# Monitor temperature
watch -n 30 'vcgencmd measure_temp'
```

## 📚 Additional Resources

- [Assembly Guide](assembly_guide.md)
- [Calibration Guide](calibration_guide.md)
- [Configuration Reference](configuration.md)
- [API Documentation](api_docs.md)
- [Hardware Specifications](hardware_specs.md)

---

**Remember**: Most issues can be resolved by checking the basics first - power, connections, and configuration. When in doubt, start with the diagnostic commands and work your way up to more complex solutions. 