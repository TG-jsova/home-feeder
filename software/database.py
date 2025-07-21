#!/usr/bin/env python3
"""
Database Interface
Handles SQLite database operations for event logging and data storage.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = 'cat_feeder.db'):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        data TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create weight_readings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weight_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        weight REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create feeding_records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feeding_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        portion REAL NOT NULL,
                        cat_weight REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create system_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_weight_timestamp ON weight_readings(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feeding_timestamp ON feeding_records(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def log_event(self, event_type: str, data: Dict[str, Any] = None):
        """
        Log an event to the database
        
        Args:
            event_type: Type of event (e.g., 'feeding', 'cat_detected', 'error')
            data: Additional event data as dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data_json = json.dumps(data) if data else None
                
                cursor.execute('''
                    INSERT INTO events (type, data, timestamp)
                    VALUES (?, ?, ?)
                ''', (event_type, data_json, datetime.now().isoformat()))
                
                conn.commit()
                logger.debug(f"Logged event: {event_type}")
                
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    def log_weight_reading(self, weight: float):
        """
        Log a weight reading
        
        Args:
            weight: Weight in kilograms
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO weight_readings (weight, timestamp)
                    VALUES (?, ?)
                ''', (weight, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log weight reading: {e}")
    
    def log_feeding(self, portion: float, cat_weight: Optional[float] = None):
        """
        Log a feeding event
        
        Args:
            portion: Portion dispensed in grams
            cat_weight: Cat weight at feeding time (optional)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO feeding_records (portion, cat_weight, timestamp)
                    VALUES (?, ?, ?)
                ''', (portion, cat_weight, datetime.now().isoformat()))
                
                conn.commit()
                logger.info(f"Logged feeding: {portion}g")
                
        except Exception as e:
            logger.error(f"Failed to log feeding: {e}")
    
    def log_system_message(self, level: str, message: str):
        """
        Log a system message
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_logs (level, message, timestamp)
                    VALUES (?, ?, ?)
                ''', (level, message, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log system message: {e}")
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT type, data, timestamp
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                events = []
                for row in cursor.fetchall():
                    event = {
                        'type': row['type'],
                        'timestamp': row['timestamp'],
                        'data': json.loads(row['data']) if row['data'] else None
                    }
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            return []
    
    def get_weight_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get weight history for specified hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of weight readings
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT weight, timestamp
                    FROM weight_readings
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (cutoff_time.isoformat(),))
                
                readings = []
                for row in cursor.fetchall():
                    reading = {
                        'weight': row['weight'],
                        'timestamp': row['timestamp']
                    }
                    readings.append(reading)
                
                return readings
                
        except Exception as e:
            logger.error(f"Failed to get weight history: {e}")
            return []
    
    def get_feeding_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get feeding history for specified days
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of feeding records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT portion, cat_weight, timestamp
                    FROM feeding_records
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
                
                feedings = []
                for row in cursor.fetchall():
                    feeding = {
                        'portion': row['portion'],
                        'cat_weight': row['cat_weight'],
                        'timestamp': row['timestamp']
                    }
                    feedings.append(feeding)
                
                return feedings
                
        except Exception as e:
            logger.error(f"Failed to get feeding history: {e}")
            return []
    
    def get_system_logs(self, hours: int = 24, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get system logs
        
        Args:
            hours: Number of hours to look back
            level: Filter by log level (optional)
            
        Returns:
            List of log entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                if level:
                    cursor.execute('''
                        SELECT level, message, timestamp
                        FROM system_logs
                        WHERE timestamp >= ? AND level = ?
                        ORDER BY timestamp DESC
                    ''', (cutoff_time.isoformat(), level))
                else:
                    cursor.execute('''
                        SELECT level, message, timestamp
                        FROM system_logs
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                    ''', (cutoff_time.isoformat(),))
                
                logs = []
                for row in cursor.fetchall():
                    log_entry = {
                        'level': row['level'],
                        'message': row['message'],
                        'timestamp': row['timestamp']
                    }
                    logs.append(log_entry)
                
                return logs
                
        except Exception as e:
            logger.error(f"Failed to get system logs: {e}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get system statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary of statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Total feedings
                cursor.execute('''
                    SELECT COUNT(*), SUM(portion)
                    FROM feeding_records
                    WHERE timestamp >= ?
                ''', (cutoff_time.isoformat(),))
                
                feeding_count, total_portion = cursor.fetchone()
                feeding_count = feeding_count or 0
                total_portion = total_portion or 0
                
                # Average cat weight
                cursor.execute('''
                    SELECT AVG(cat_weight)
                    FROM feeding_records
                    WHERE timestamp >= ? AND cat_weight IS NOT NULL
                ''', (cutoff_time.isoformat(),))
                
                avg_weight = cursor.fetchone()[0] or 0
                
                # Cat detection count
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM events
                    WHERE type = 'cat_detected' AND timestamp >= ?
                ''', (cutoff_time.isoformat(),))
                
                cat_detections = cursor.fetchone()[0] or 0
                
                # Error count
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM events
                    WHERE type = 'error' AND timestamp >= ?
                ''', (cutoff_time.isoformat(),))
                
                error_count = cursor.fetchone()[0] or 0
                
                return {
                    'feeding_count': feeding_count,
                    'total_portion': total_portion,
                    'avg_cat_weight': avg_weight,
                    'cat_detections': cat_detections,
                    'error_count': error_count,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old data to prevent database bloat
        
        Args:
            days: Keep data newer than this many days
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Delete old events
                cursor.execute('DELETE FROM events WHERE timestamp < ?', (cutoff_time.isoformat(),))
                events_deleted = cursor.rowcount
                
                # Delete old weight readings (keep more recent ones)
                cursor.execute('DELETE FROM weight_readings WHERE timestamp < ?', (cutoff_time.isoformat(),))
                weight_deleted = cursor.rowcount
                
                # Delete old system logs
                cursor.execute('DELETE FROM system_logs WHERE timestamp < ?', (cutoff_time.isoformat(),))
                logs_deleted = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleaned up old data: {events_deleted} events, {weight_deleted} weight readings, {logs_deleted} logs")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def export_data(self, export_path: str):
        """
        Export database to JSON file
        
        Args:
            export_path: Path to export file
        """
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'events': self.get_recent_events(1000),
                'feeding_history': self.get_feeding_history(30),
                'weight_history': self.get_weight_history(168),  # 7 days
                'statistics': self.get_statistics(30)
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Data exported to {export_path}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
    
    def get_database_size(self) -> int:
        """
        Get database file size in bytes
        
        Returns:
            Database file size
        """
        try:
            return Path(self.db_path).stat().st_size
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return 0 