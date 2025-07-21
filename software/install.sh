#!/bin/bash

# Automated Cat Feeder Installation Script
# This script sets up the cat feeder system on a Raspberry Pi

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/home-feeder.git"
INSTALL_DIR="/opt/cat-feeder"
SERVICE_NAME="cat-feeder"
USER_NAME="catfeeder"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        print_warning "This script is designed for Raspberry Pi. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    apt update && apt upgrade -y
    print_success "System updated"
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages..."
    
    # Essential packages
    apt install -y python3 python3-pip python3-venv git curl wget
    
    # GPIO and hardware support
    apt install -y python3-rpi.gpio python3-smbus i2c-tools
    
    # Additional utilities
    apt install -y htop vim nano screen
    
    print_success "Packages installed"
}

# Function to enable I2C
enable_i2c() {
    print_status "Enabling I2C interface..."
    
    # Enable I2C in raspi-config
    raspi-config nonint do_i2c 0
    
    # Add user to i2c group
    usermod -a -G i2c $SUDO_USER
    
    print_success "I2C enabled"
}

# Function to create system user
create_user() {
    print_status "Creating system user..."
    
    if id "$USER_NAME" &>/dev/null; then
        print_warning "User $USER_NAME already exists"
    else
        useradd -r -s /bin/bash -d $INSTALL_DIR $USER_NAME
        print_success "User $USER_NAME created"
    fi
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory already exists. Backup and replace? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mv $INSTALL_DIR ${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi
    
    git clone $REPO_URL $INSTALL_DIR
    chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
    print_success "Repository cloned"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd $INSTALL_DIR/software
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install requirements
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Function to create systemd service
create_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Automated Cat Feeder
After=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR/software
Environment=PATH=$INSTALL_DIR/software/venv/bin
ExecStart=$INSTALL_DIR/software/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    
    print_success "Systemd service created and enabled"
}

# Function to setup logging
setup_logging() {
    print_status "Setting up logging..."
    
    # Create log directory
    mkdir -p /var/log/cat-feeder
    chown $USER_NAME:$USER_NAME /var/log/cat-feeder
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/cat-feeder << EOF
/var/log/cat-feeder/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER_NAME $USER_NAME
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF
    
    print_success "Logging setup complete"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Allow web interface port
    ufw allow 5000/tcp comment "Cat Feeder Web Interface"
    
    # Allow SSH (if not already allowed)
    ufw allow ssh
    
    print_success "Firewall configured"
}

# Function to create configuration
create_config() {
    print_status "Creating initial configuration..."
    
    cd $INSTALL_DIR/software
    
    # Copy default config if it doesn't exist
    if [ ! -f config.json ]; then
        cp config.json.example config.json 2>/dev/null || {
            print_warning "No example config found, creating basic config"
            cat > config.json << EOF
{
  "weight_sensor": {
    "dout_pin": 5,
    "sck_pin": 6,
    "calibration_factor": 2280.0
  },
  "servo": {
    "pin": 18,
    "feeding_angle": 90
  },
  "web_interface": {
    "host": "0.0.0.0",
    "port": 5000
  }
}
EOF
        }
    fi
    
    chown $USER_NAME:$USER_NAME config.json
    print_success "Configuration created"
}

# Function to setup backup
setup_backup() {
    print_status "Setting up backup system..."
    
    # Create backup directory
    mkdir -p /var/backups/cat-feeder
    chown $USER_NAME:$USER_NAME /var/backups/cat-feeder
    
    # Create backup script
    cat > $INSTALL_DIR/backup.sh << EOF
#!/bin/bash
# Backup script for cat feeder

BACKUP_DIR="/var/backups/cat-feeder"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cat-feeder-backup-\$DATE.tar.gz"

cd $INSTALL_DIR
tar -czf \$BACKUP_DIR/\$BACKUP_FILE software/ --exclude=software/venv

# Keep only last 7 backups
cd \$BACKUP_DIR
ls -t | tail -n +8 | xargs -r rm

echo "Backup created: \$BACKUP_FILE"
EOF
    
    chmod +x $INSTALL_DIR/backup.sh
    chown $USER_NAME:$USER_NAME $INSTALL_DIR/backup.sh
    
    # Add to crontab
    (crontab -u $USER_NAME -l 2>/dev/null; echo "0 2 * * * $INSTALL_DIR/backup.sh") | crontab -u $USER_NAME -
    
    print_success "Backup system configured"
}

# Function to run initial tests
run_tests() {
    print_status "Running initial tests..."
    
    cd $INSTALL_DIR/software
    
    # Test Python imports
    source venv/bin/activate
    python -c "
import sys
sys.path.append('.')
try:
    from weight_sensor import WeightSensor
    from feeder_controller import FeederController
    from database import Database
    print('✓ All modules imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    print_success "Initial tests passed"
}

# Function to display post-installation information
display_info() {
    print_success "Installation completed successfully!"
    echo
    echo "=== Post-Installation Information ==="
    echo
    echo "Service Management:"
    echo "  Start service:   sudo systemctl start $SERVICE_NAME"
    echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
    echo "  Status:          sudo systemctl status $SERVICE_NAME"
    echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
    echo
    echo "Configuration:"
    echo "  Config file:     $INSTALL_DIR/software/config.json"
    echo "  Logs:            /var/log/cat-feeder/"
    echo "  Database:        $INSTALL_DIR/software/cat_feeder.db"
    echo
    echo "Web Interface:"
    echo "  URL:             http://$(hostname -I | awk '{print $1}'):5000"
    echo
    echo "Next Steps:"
    echo "  1. Configure hardware connections (see docs/assembly_guide.md)"
    echo "  2. Calibrate weight sensor and feeder"
    echo "  3. Start the service: sudo systemctl start $SERVICE_NAME"
    echo "  4. Access web interface to configure feeding schedules"
    echo
    echo "Documentation:"
    echo "  Assembly Guide:  $INSTALL_DIR/docs/assembly_guide.md"
    echo "  Calibration:     $INSTALL_DIR/docs/calibration_guide.md"
    echo
}

# Function to cleanup on error
cleanup() {
    print_error "Installation failed. Cleaning up..."
    
    # Stop and disable service if it exists
    systemctl stop $SERVICE_NAME 2>/dev/null || true
    systemctl disable $SERVICE_NAME 2>/dev/null || true
    rm -f /etc/systemd/system/$SERVICE_NAME.service
    
    # Remove installation directory if it was created
    if [ -d "$INSTALL_DIR" ] && [ ! -d "${INSTALL_DIR}.backup" ]; then
        rm -rf $INSTALL_DIR
    fi
    
    print_error "Cleanup complete"
}

# Main installation function
main() {
    print_status "Starting Automated Cat Feeder installation..."
    
    # Set up error handling
    trap cleanup ERR
    
    # Run installation steps
    check_root
    check_raspberry_pi
    update_system
    install_packages
    enable_i2c
    create_user
    clone_repository
    setup_python_env
    create_service
    setup_logging
    setup_firewall
    create_config
    setup_backup
    run_tests
    
    # Display completion information
    display_info
    
    print_success "Installation completed successfully!"
}

# Run main function
main "$@" 