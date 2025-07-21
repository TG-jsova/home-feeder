#!/usr/bin/env python3
"""
Backup and Restore Utility
Handles backup and restore operations for the cat feeder system
"""

import os
import json
import shutil
import sqlite3
import logging
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup and restore operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backup manager
        
        Args:
            config: System configuration
        """
        self.config = config
        self.backup_dir = Path("/var/backups/cat-feeder")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup settings
        self.max_backups = 7
        self.backup_format = "tar.gz"  # or "zip"
    
    def create_backup(self, include_logs: bool = True, include_database: bool = True) -> str:
        """
        Create a complete backup of the system
        
        Args:
            include_logs: Include log files in backup
            include_database: Include database in backup
            
        Returns:
            Path to backup file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cat-feeder-backup-{timestamp}.{self.backup_format}"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Creating backup: {backup_filename}")
            
            # Create backup archive
            if self.backup_format == "tar.gz":
                self._create_tar_backup(backup_path, include_logs, include_database)
            else:
                self._create_zip_backup(backup_path, include_logs, include_database)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def _create_tar_backup(self, backup_path: Path, include_logs: bool, include_database: bool):
        """Create tar.gz backup"""
        with tarfile.open(backup_path, "w:gz") as tar:
            # Add software directory (excluding venv)
            software_dir = Path(".")
            for item in software_dir.rglob("*"):
                if item.is_file() and "venv" not in str(item):
                    tar.add(item, arcname=f"software/{item.relative_to(software_dir)}")
            
            # Add configuration
            if Path("config.json").exists():
                tar.add("config.json", arcname="config.json")
            
            # Add database
            if include_database:
                db_path = self.config.get('database', {}).get('path', 'cat_feeder.db')
                if Path(db_path).exists():
                    tar.add(db_path, arcname=f"database/{Path(db_path).name}")
            
            # Add logs
            if include_logs:
                log_dir = Path("/var/log/cat-feeder")
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        tar.add(log_file, arcname=f"logs/{log_file.name}")
            
            # Add metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'includes': {
                    'logs': include_logs,
                    'database': include_database
                },
                'config': self.config
            }
            
            # Write metadata to temporary file
            metadata_file = Path("backup_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            tar.add(metadata_file, arcname="backup_metadata.json")
            metadata_file.unlink()  # Clean up temporary file
    
    def _create_zip_backup(self, backup_path: Path, include_logs: bool, include_database: bool):
        """Create zip backup"""
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add software directory (excluding venv)
            software_dir = Path(".")
            for item in software_dir.rglob("*"):
                if item.is_file() and "venv" not in str(item):
                    zipf.write(item, f"software/{item.relative_to(software_dir)}")
            
            # Add configuration
            if Path("config.json").exists():
                zipf.write("config.json", "config.json")
            
            # Add database
            if include_database:
                db_path = self.config.get('database', {}).get('path', 'cat_feeder.db')
                if Path(db_path).exists():
                    zipf.write(db_path, f"database/{Path(db_path).name}")
            
            # Add logs
            if include_logs:
                log_dir = Path("/var/log/cat-feeder")
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        zipf.write(log_file, f"logs/{log_file.name}")
            
            # Add metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'includes': {
                    'logs': include_logs,
                    'database': include_database
                },
                'config': self.config
            }
            
            # Write metadata to temporary file
            metadata_file = Path("backup_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            zipf.write(metadata_file, "backup_metadata.json")
            metadata_file.unlink()  # Clean up temporary file
    
    def restore_backup(self, backup_path: str, restore_database: bool = True, 
                      restore_config: bool = True, restore_logs: bool = False) -> bool:
        """
        Restore from backup
        
        Args:
            backup_path: Path to backup file
            restore_database: Restore database
            restore_config: Restore configuration
            restore_logs: Restore log files
            
        Returns:
            True if restore successful
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            logger.info(f"Restoring from backup: {backup_path}")
            
            # Extract backup
            temp_dir = Path("/tmp/cat-feeder-restore")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                if backup_file.suffix == '.gz':
                    with tarfile.open(backup_file, "r:gz") as tar:
                        tar.extractall(temp_dir)
                else:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        zipf.extractall(temp_dir)
                
                # Read metadata
                metadata_file = temp_dir / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    logger.info(f"Backup created: {metadata['timestamp']}")
                
                # Restore components
                if restore_config and (temp_dir / "config.json").exists():
                    self._restore_config(temp_dir / "config.json")
                
                if restore_database and (temp_dir / "database").exists():
                    self._restore_database(temp_dir / "database")
                
                if restore_logs and (temp_dir / "logs").exists():
                    self._restore_logs(temp_dir / "logs")
                
                # Restore software files (if needed)
                if (temp_dir / "software").exists():
                    self._restore_software(temp_dir / "software")
                
                logger.info("Backup restored successfully")
                return True
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def _restore_config(self, config_file: Path):
        """Restore configuration file"""
        try:
            # Backup current config
            if Path("config.json").exists():
                backup_name = f"config.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2("config.json", backup_name)
                logger.info(f"Current config backed up as {backup_name}")
            
            # Restore config
            shutil.copy2(config_file, "config.json")
            logger.info("Configuration restored")
            
        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")
            raise
    
    def _restore_database(self, db_dir: Path):
        """Restore database"""
        try:
            for db_file in db_dir.glob("*.db"):
                # Backup current database
                if Path(db_file.name).exists():
                    backup_name = f"{db_file.name}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(db_file.name, backup_name)
                    logger.info(f"Current database backed up as {backup_name}")
                
                # Restore database
                shutil.copy2(db_file, db_file.name)
                logger.info(f"Database {db_file.name} restored")
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise
    
    def _restore_logs(self, logs_dir: Path):
        """Restore log files"""
        try:
            log_dir = Path("/var/log/cat-feeder")
            log_dir.mkdir(exist_ok=True)
            
            for log_file in logs_dir.glob("*.log"):
                shutil.copy2(log_file, log_dir / log_file.name)
                logger.info(f"Log file {log_file.name} restored")
            
        except Exception as e:
            logger.error(f"Failed to restore logs: {e}")
            raise
    
    def _restore_software(self, software_dir: Path):
        """Restore software files"""
        try:
            # Only restore specific files, not the entire directory
            files_to_restore = [
                "main.py",
                "requirements.txt",
                "test_system.py"
            ]
            
            for file_name in files_to_restore:
                source_file = software_dir / file_name
                if source_file.exists():
                    # Backup current file
                    if Path(file_name).exists():
                        backup_name = f"{file_name}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(file_name, backup_name)
                        logger.info(f"Current {file_name} backed up as {backup_name}")
                    
                    # Restore file
                    shutil.copy2(source_file, file_name)
                    logger.info(f"Software file {file_name} restored")
            
        except Exception as e:
            logger.error(f"Failed to restore software files: {e}")
            raise
    
    def _cleanup_old_backups(self):
        """Remove old backups, keeping only the most recent ones"""
        try:
            backup_files = list(self.backup_dir.glob(f"*.{self.backup_format}"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup_file in backup_files[self.max_backups:]:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob(f"*.{self.backup_format}"):
                stat = backup_file.stat()
                backup_info = {
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                }
                backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return None
            
            # Extract metadata
            temp_dir = Path("/tmp/cat-feeder-info")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                if backup_file.suffix == '.gz':
                    with tarfile.open(backup_file, "r:gz") as tar:
                        tar.extractall(temp_dir, members=[tar.getmember("backup_metadata.json")])
                else:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        zipf.extract("backup_metadata.json", temp_dir)
                
                metadata_file = temp_dir / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    stat = backup_file.stat()
                    info = {
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'size_mb': stat.st_size / (1024 * 1024),
                        'created': metadata['timestamp'],
                        'version': metadata['version'],
                        'includes': metadata['includes']
                    }
                    return info
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return None
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return False
            
            logger.info(f"Verifying backup: {backup_path}")
            
            # Test archive integrity
            if backup_file.suffix == '.gz':
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.getmembers()  # This will raise an error if corrupted
            else:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.testzip()  # This will raise an error if corrupted
            
            # Check for required files
            temp_dir = Path("/tmp/cat-feeder-verify")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                if backup_file.suffix == '.gz':
                    with tarfile.open(backup_file, "r:gz") as tar:
                        tar.extractall(temp_dir)
                else:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        zipf.extractall(temp_dir)
                
                # Check for metadata
                if not (temp_dir / "backup_metadata.json").exists():
                    logger.error("Backup missing metadata")
                    return False
                
                # Check for software files
                if not (temp_dir / "software").exists():
                    logger.error("Backup missing software files")
                    return False
                
                logger.info("Backup verification successful")
                return True
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False

def main():
    """Command line interface for backup operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cat Feeder Backup and Restore Utility")
    parser.add_argument('action', choices=['create', 'restore', 'list', 'info', 'verify'],
                       help='Action to perform')
    parser.add_argument('--backup-file', '-f', help='Backup file path (for restore/info/verify)')
    parser.add_argument('--no-logs', action='store_true', help='Exclude logs from backup')
    parser.add_argument('--no-database', action='store_true', help='Exclude database from backup')
    parser.add_argument('--restore-config', action='store_true', help='Restore configuration')
    parser.add_argument('--restore-database', action='store_true', help='Restore database')
    parser.add_argument('--restore-logs', action='store_true', help='Restore logs')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Warning: config.json not found, using default configuration")
        config = {}
    
    backup_manager = BackupManager(config)
    
    if args.action == 'create':
        include_logs = not args.no_logs
        include_database = not args.no_database
        backup_path = backup_manager.create_backup(include_logs, include_database)
        print(f"Backup created: {backup_path}")
    
    elif args.action == 'restore':
        if not args.backup_file:
            print("Error: --backup-file required for restore")
            return 1
        
        restore_config = args.restore_config
        restore_database = args.restore_database
        restore_logs = args.restore_logs
        
        # If no specific components specified, restore all
        if not any([restore_config, restore_database, restore_logs]):
            restore_config = True
            restore_database = True
            restore_logs = False
        
        success = backup_manager.restore_backup(args.backup_file, restore_database, 
                                              restore_config, restore_logs)
        if success:
            print("Backup restored successfully")
        else:
            print("Backup restore failed")
            return 1
    
    elif args.action == 'list':
        backups = backup_manager.list_backups()
        if backups:
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['filename']} ({backup['size_mb']:.1f}MB, {backup['age_days']} days old)")
        else:
            print("No backups found")
    
    elif args.action == 'info':
        if not args.backup_file:
            print("Error: --backup-file required for info")
            return 1
        
        info = backup_manager.get_backup_info(args.backup_file)
        if info:
            print("Backup information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("Could not retrieve backup information")
            return 1
    
    elif args.action == 'verify':
        if not args.backup_file:
            print("Error: --backup-file required for verify")
            return 1
        
        if backup_manager.verify_backup(args.backup_file):
            print("Backup verification successful")
        else:
            print("Backup verification failed")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 