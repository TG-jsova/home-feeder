#!/usr/bin/env python3
"""
Health Monitor
Monitors system health and provides alerts for issues
"""

import time
import threading
import logging
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitors system health and performance"""
    
    def __init__(self, database, config: Dict[str, Any]):
        """
        Initialize health monitor
        
        Args:
            database: Database instance
            config: System configuration
        """
        self.database = database
        self.config = config
        self.running = False
        self.health_thread = None
        
        # Health metrics
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'temperature': [],
            'uptime': 0,
            'last_check': None
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_usage': 80.0,  # %
            'memory_usage': 85.0,  # %
            'disk_usage': 90.0,  # %
            'temperature': 70.0,  # °C
            'database_size_mb': 100,  # MB
            'log_size_mb': 50,  # MB
        }
        
        # Alert history
        self.alerts = []
        self.max_alerts = 100
    
    def start(self):
        """Start health monitoring"""
        if self.running:
            logger.warning("Health monitor is already running")
            return
        
        self.running = True
        self.health_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.health_thread.start()
        logger.info("Health monitor started")
    
    def stop(self):
        """Stop health monitoring"""
        self.running = False
        if self.health_thread:
            self.health_thread.join(timeout=5)
        logger.info("Health monitor stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._collect_metrics()
                self._check_thresholds()
                self._cleanup_old_data()
                
                # Sleep for configured interval
                interval = self.config.get('maintenance', {}).get('health_check_interval_minutes', 30)
                time.sleep(interval * 60)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _collect_metrics(self):
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append({
                'value': cpu_percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append({
                'value': memory.percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics['disk_usage'].append({
                'value': disk_percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Temperature (if available)
            try:
                temp = self._get_cpu_temperature()
                if temp is not None:
                    self.metrics['temperature'].append({
                        'value': temp,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.debug(f"Could not read temperature: {e}")
            
            # Uptime
            self.metrics['uptime'] = time.time() - psutil.boot_time()
            self.metrics['last_check'] = datetime.now().isoformat()
            
            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            for metric_type in ['cpu_usage', 'memory_usage', 'disk_usage', 'temperature']:
                self.metrics[metric_type] = [
                    m for m in self.metrics[metric_type]
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
            
            logger.debug("Health metrics collected")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius"""
        try:
            # Try different temperature file locations
            temp_files = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/hwmon/hwmon0/temp1_input',
                '/sys/class/hwmon/hwmon1/temp1_input'
            ]
            
            for temp_file in temp_files:
                if Path(temp_file).exists():
                    with open(temp_file, 'r') as f:
                        temp_raw = int(f.read().strip())
                        return temp_raw / 1000.0  # Convert millidegrees to degrees
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not read CPU temperature: {e}")
            return None
    
    def _check_thresholds(self):
        """Check if any metrics exceed thresholds"""
        try:
            # Check CPU usage
            if self.metrics['cpu_usage']:
                latest_cpu = self.metrics['cpu_usage'][-1]['value']
                if latest_cpu > self.thresholds['cpu_usage']:
                    self._create_alert('high_cpu_usage', f"CPU usage: {latest_cpu:.1f}%")
            
            # Check memory usage
            if self.metrics['memory_usage']:
                latest_memory = self.metrics['memory_usage'][-1]['value']
                if latest_memory > self.thresholds['memory_usage']:
                    self._create_alert('high_memory_usage', f"Memory usage: {latest_memory:.1f}%")
            
            # Check disk usage
            if self.metrics['disk_usage']:
                latest_disk = self.metrics['disk_usage'][-1]['value']
                if latest_disk > self.thresholds['disk_usage']:
                    self._create_alert('high_disk_usage', f"Disk usage: {latest_disk:.1f}%")
            
            # Check temperature
            if self.metrics['temperature']:
                latest_temp = self.metrics['temperature'][-1]['value']
                if latest_temp > self.thresholds['temperature']:
                    self._create_alert('high_temperature', f"CPU temperature: {latest_temp:.1f}°C")
            
            # Check database size
            db_size = self._get_database_size()
            if db_size > self.thresholds['database_size_mb']:
                self._create_alert('large_database', f"Database size: {db_size:.1f}MB")
            
            # Check log file size
            log_size = self._get_log_size()
            if log_size > self.thresholds['log_size_mb']:
                self._create_alert('large_log_file', f"Log file size: {log_size:.1f}MB")
            
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
    
    def _create_alert(self, alert_type: str, message: str):
        """Create and log an alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'warning'
        }
        
        # Determine severity
        if alert_type in ['high_temperature', 'high_disk_usage']:
            alert['severity'] = 'critical'
        elif alert_type in ['high_cpu_usage', 'high_memory_usage']:
            alert['severity'] = 'warning'
        else:
            alert['severity'] = 'info'
        
        # Add to alerts list
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Log to database
        self.database.log_event('health_alert', alert)
        
        # Log to console
        log_level = logging.ERROR if alert['severity'] == 'critical' else logging.WARNING
        logger.log(log_level, f"Health alert: {message}")
    
    def _get_database_size(self) -> float:
        """Get database file size in MB"""
        try:
            db_path = self.config.get('database', {}).get('path', 'cat_feeder.db')
            if Path(db_path).exists():
                size_bytes = Path(db_path).stat().st_size
                return size_bytes / (1024 * 1024)  # Convert to MB
            return 0.0
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0.0
    
    def _get_log_size(self) -> float:
        """Get log file size in MB"""
        try:
            log_file = self.config.get('logging', {}).get('file', 'cat_feeder.log')
            if Path(log_file).exists():
                size_bytes = Path(log_file).stat().st_size
                return size_bytes / (1024 * 1024)  # Convert to MB
            return 0.0
        except Exception as e:
            logger.error(f"Error getting log file size: {e}")
            return 0.0
    
    def _cleanup_old_data(self):
        """Clean up old health data"""
        try:
            # Clean up old metrics (keep last 7 days)
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for metric_type in ['cpu_usage', 'memory_usage', 'disk_usage', 'temperature']:
                self.metrics[metric_type] = [
                    m for m in self.metrics[metric_type]
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
            
            # Clean up old alerts (keep last 30 days)
            cutoff_time = datetime.now() - timedelta(days=30)
            self.alerts = [
                alert for alert in self.alerts
                if datetime.fromisoformat(alert['timestamp']) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        try:
            # Calculate averages for recent metrics
            cpu_avg = self._calculate_average('cpu_usage', 10)
            memory_avg = self._calculate_average('memory_usage', 10)
            disk_avg = self._calculate_average('disk_usage', 10)
            temp_avg = self._calculate_average('temperature', 10)
            
            # Get latest values
            latest_cpu = self.metrics['cpu_usage'][-1]['value'] if self.metrics['cpu_usage'] else 0
            latest_memory = self.metrics['memory_usage'][-1]['value'] if self.metrics['memory_usage'] else 0
            latest_disk = self.metrics['disk_usage'][-1]['value'] if self.metrics['disk_usage'] else 0
            latest_temp = self.metrics['temperature'][-1]['value'] if self.metrics['temperature'] else None
            
            return {
                'status': 'healthy' if self._is_healthy() else 'warning',
                'uptime_seconds': self.metrics['uptime'],
                'last_check': self.metrics['last_check'],
                'cpu': {
                    'current': latest_cpu,
                    'average': cpu_avg,
                    'threshold': self.thresholds['cpu_usage']
                },
                'memory': {
                    'current': latest_memory,
                    'average': memory_avg,
                    'threshold': self.thresholds['memory_usage']
                },
                'disk': {
                    'current': latest_disk,
                    'average': disk_avg,
                    'threshold': self.thresholds['disk_usage']
                },
                'temperature': {
                    'current': latest_temp,
                    'average': temp_avg,
                    'threshold': self.thresholds['temperature']
                },
                'database_size_mb': self._get_database_size(),
                'log_size_mb': self._get_log_size(),
                'recent_alerts': self.alerts[-10:] if self.alerts else []
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_average(self, metric_type: str, count: int) -> float:
        """Calculate average of recent metric values"""
        try:
            metrics = self.metrics[metric_type][-count:]
            if not metrics:
                return 0.0
            
            total = sum(m['value'] for m in metrics)
            return total / len(metrics)
            
        except Exception as e:
            logger.error(f"Error calculating average for {metric_type}: {e}")
            return 0.0
    
    def _is_healthy(self) -> bool:
        """Check if system is healthy"""
        try:
            # Check if any metrics exceed thresholds
            if self.metrics['cpu_usage'] and self.metrics['cpu_usage'][-1]['value'] > self.thresholds['cpu_usage']:
                return False
            
            if self.metrics['memory_usage'] and self.metrics['memory_usage'][-1]['value'] > self.thresholds['memory_usage']:
                return False
            
            if self.metrics['disk_usage'] and self.metrics['disk_usage'][-1]['value'] > self.thresholds['disk_usage']:
                return False
            
            if self.metrics['temperature'] and self.metrics['temperature'][-1]['value'] > self.thresholds['temperature']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking health status: {e}")
            return False
    
    def get_metrics_history(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics history for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            history = {}
            for metric_type in ['cpu_usage', 'memory_usage', 'disk_usage', 'temperature']:
                history[metric_type] = [
                    m for m in self.metrics[metric_type]
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting metrics history: {e}")
            return {}
    
    def reset_alerts(self):
        """Reset all alerts"""
        self.alerts = []
        logger.info("Health alerts reset")

class HealthReporter:
    """Generates health reports"""
    
    def __init__(self, health_monitor: HealthMonitor):
        self.health_monitor = health_monitor
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily health report"""
        try:
            status = self.health_monitor.get_health_status()
            metrics_history = self.health_monitor.get_metrics_history(24)
            
            # Calculate statistics
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'overall_status': status['status'],
                'uptime_hours': status['uptime_seconds'] / 3600,
                'alerts_count': len(status['recent_alerts']),
                'metrics_summary': {},
                'recommendations': []
            }
            
            # Add metrics summary
            for metric_type, history in metrics_history.items():
                if history:
                    values = [m['value'] for m in history]
                    report['metrics_summary'][metric_type] = {
                        'min': min(values),
                        'max': max(values),
                        'average': sum(values) / len(values),
                        'samples': len(values)
                    }
            
            # Generate recommendations
            recommendations = []
            
            if status['cpu']['average'] > 70:
                recommendations.append("Consider optimizing CPU usage or upgrading hardware")
            
            if status['memory']['average'] > 80:
                recommendations.append("Consider increasing memory or optimizing memory usage")
            
            if status['disk']['current'] > 85:
                recommendations.append("Consider cleaning up disk space or expanding storage")
            
            if status['temperature']['current'] and status['temperature']['current'] > 65:
                recommendations.append("Consider improving cooling or reducing load")
            
            if status['database_size_mb'] > 50:
                recommendations.append("Consider cleaning up old database records")
            
            if status['log_size_mb'] > 25:
                recommendations.append("Consider rotating log files")
            
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return {'error': str(e)}
    
    def export_report(self, report: Dict[str, Any], format: str = 'json') -> str:
        """Export report in specified format"""
        try:
            if format.lower() == 'json':
                import json
                return json.dumps(report, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(['Metric', 'Min', 'Max', 'Average', 'Samples'])
                
                # Write metrics
                for metric_type, data in report['metrics_summary'].items():
                    writer.writerow([
                        metric_type,
                        data['min'],
                        data['max'],
                        data['average'],
                        data['samples']
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return f"Error: {str(e)}" 