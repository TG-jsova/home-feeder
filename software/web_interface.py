#!/usr/bin/env python3
"""
Web Interface
Flask-based web server for controlling and monitoring the cat feeder
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

class WebInterface:
    def __init__(self, cat_feeder):
        """Initialize web interface"""
        self.cat_feeder = cat_feeder
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'cat-feeder-secret-key'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cat_feeder.db'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.db = SQLAlchemy(self.app)
        self._setup_routes()
        self._setup_templates()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard"""
            status = self.cat_feeder.get_status()
            recent_events = self.cat_feeder.database.get_recent_events(10)
            return render_template('index.html', status=status, events=recent_events)
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status as JSON"""
            return jsonify(self.cat_feeder.get_status())
        
        @self.route('/api/feed', methods=['POST'])
        def api_feed():
            """Trigger manual feeding"""
            try:
                data = request.get_json()
                portion = data.get('portion', 50)  # Default 50g
                
                success = self.cat_feeder.feed_cat(portion)
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error in manual feeding: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/feed_manual', methods=['POST'])
        def api_feed_manual():
            """Manual feeding with duration"""
            try:
                data = request.get_json()
                duration = data.get('duration', 2.0)  # Default 2 seconds
                
                success = self.cat_feeder.feeder_controller.dispense_food_manual(duration)
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error in manual feeding: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/tare', methods=['POST'])
        def api_tare():
            """Tare the weight sensor"""
            try:
                success = self.cat_feeder.weight_sensor.tare()
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error taring scale: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/calibrate', methods=['POST'])
        def api_calibrate():
            """Calibrate weight sensor"""
            try:
                data = request.get_json()
                known_weight = data.get('known_weight')
                
                if not known_weight:
                    return jsonify({'success': False, 'error': 'Known weight required'})
                
                success = self.cat_feeder.weight_sensor.calibrate(known_weight)
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error calibrating: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/schedules', methods=['GET', 'POST'])
        def api_schedules():
            """Get or update feeding schedules"""
            if request.method == 'GET':
                return jsonify(self.cat_feeder.feeding_schedules)
            else:
                try:
                    data = request.get_json()
                    self.cat_feeder.feeding_schedules = data
                    self.cat_feeder.update_config({'feeding_schedules': data})
                    return jsonify({'success': True})
                except Exception as e:
                    logger.error(f"Error updating schedules: {e}")
                    return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/events')
        def api_events():
            """Get recent events"""
            try:
                limit = request.args.get('limit', 50, type=int)
                events = self.cat_feeder.database.get_recent_events(limit)
                return jsonify(events)
            except Exception as e:
                logger.error(f"Error getting events: {e}")
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/config', methods=['GET', 'POST'])
        def api_config():
            """Get or update configuration"""
            if request.method == 'GET':
                return jsonify(self.cat_feeder.config)
            else:
                try:
                    data = request.get_json()
                    self.cat_feeder.update_config(data)
                    return jsonify({'success': True})
                except Exception as e:
                    logger.error(f"Error updating config: {e}")
                    return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/weight_history')
        def api_weight_history():
            """Get weight history data"""
            try:
                hours = request.args.get('hours', 24, type=int)
                events = self.cat_feeder.database.get_weight_history(hours)
                return jsonify(events)
            except Exception as e:
                logger.error(f"Error getting weight history: {e}")
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/feeding_history')
        def api_feeding_history():
            """Get feeding history data"""
            try:
                days = request.args.get('days', 7, type=int)
                events = self.cat_feeder.database.get_feeding_history(days)
                return jsonify(events)
            except Exception as e:
                logger.error(f"Error getting feeding history: {e}")
                return jsonify({'error': str(e)})
    
    def _setup_templates(self):
        """Setup HTML templates"""
        
        # Create templates directory
        import os
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create base template
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Cat Feeder{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-card { transition: all 0.3s ease; }
        .status-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .weight-display { font-size: 2rem; font-weight: bold; }
        .feeding-button { min-width: 120px; }
        .event-list { max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-cat me-2"></i>Cat Feeder
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Dashboard</a>
                <a class="nav-link" href="/config"><i class="fas fa-cog me-1"></i>Settings</a>
                <a class="nav-link" href="/history"><i class="fas fa-history me-1"></i>History</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
        
        # Create index template
        index_template = '''{% extends "base.html" %}

{% block title %}Dashboard - Cat Feeder{% endblock %}

{% block content %}
<div class="row">
    <!-- Status Cards -->
    <div class="col-md-4 mb-4">
        <div class="card status-card h-100">
            <div class="card-body text-center">
                <i class="fas fa-weight-hanging fa-3x text-primary mb-3"></i>
                <h5 class="card-title">Current Weight</h5>
                <div class="weight-display text-primary" id="current-weight">
                    {{ "%.2f"|format(status.current_weight) }} kg
                </div>
                <small class="text-muted" id="weight-status">
                    {% if status.cat_present %}
                        <span class="text-success"><i class="fas fa-cat"></i> Cat Detected</span>
                    {% else %}
                        <span class="text-muted">No cat present</span>
                    {% endif %}
                </small>
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-4">
        <div class="card status-card h-100">
            <div class="card-body text-center">
                <i class="fas fa-clock fa-3x text-info mb-3"></i>
                <h5 class="card-title">Last Feeding</h5>
                <div class="h4 text-info" id="last-feeding">
                    {% if status.last_feeding_time %}
                        {{ status.last_feeding_time.split('T')[1][:5] }}
                    {% else %}
                        Never
                    {% endif %}
                </div>
                <small class="text-muted">Today</small>
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-4">
        <div class="card status-card h-100">
            <div class="card-body text-center">
                <i class="fas fa-power-off fa-3x text-success mb-3"></i>
                <h5 class="card-title">System Status</h5>
                <div class="h4 text-success" id="system-status">
                    {% if status.running %}
                        <span class="text-success">Running</span>
                    {% else %}
                        <span class="text-danger">Stopped</span>
                    {% endif %}
                </div>
                <small class="text-muted">Feeder Active</small>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Quick Actions -->
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-bolt me-2"></i>Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-6">
                        <button class="btn btn-primary feeding-button w-100" onclick="feedCat(25)">
                            <i class="fas fa-utensils me-1"></i>Feed 25g
                        </button>
                    </div>
                    <div class="col-6">
                        <button class="btn btn-success feeding-button w-100" onclick="feedCat(50)">
                            <i class="fas fa-utensils me-1"></i>Feed 50g
                        </button>
                    </div>
                    <div class="col-6">
                        <button class="btn btn-warning feeding-button w-100" onclick="feedCat(75)">
                            <i class="fas fa-utensils me-1"></i>Feed 75g
                        </button>
                    </div>
                    <div class="col-6">
                        <button class="btn btn-info feeding-button w-100" onclick="tareScale()">
                            <i class="fas fa-balance-scale me-1"></i>Tare Scale
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Feeding Schedule -->
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-calendar me-2"></i>Today's Schedule</h5>
            </div>
            <div class="card-body">
                <div id="schedule-list">
                    {% for schedule in status.feeding_schedules %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-primary">{{ schedule.time }}</span>
                        <span>{{ schedule.portion }}g</span>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" 
                                   {% if schedule.enabled %}checked{% endif %}
                                   onchange="toggleSchedule({{ loop.index0 }}, this.checked)">
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Recent Events -->
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>Recent Events</h5>
            </div>
            <div class="card-body">
                <div class="event-list" id="events-list">
                    {% for event in events %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <i class="fas fa-{{ 'utensils' if event.type == 'feeding' else 'cat' }} me-2"></i>
                            <strong>{{ event.type.title() }}</strong>
                            {% if event.data %}
                                {% if event.data.portion %}
                                    - {{ event.data.portion }}g
                                {% endif %}
                                {% if event.data.weight %}
                                    - {{ "%.2f"|format(event.data.weight) }}kg
                                {% endif %}
                            {% endif %}
                        </div>
                        <small class="text-muted">{{ event.timestamp.split('T')[1][:5] }}</small>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Update status every 2 seconds
setInterval(updateStatus, 2000);

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-weight').textContent = data.current_weight.toFixed(2) + ' kg';
            document.getElementById('weight-status').innerHTML = data.cat_present ? 
                '<span class="text-success"><i class="fas fa-cat"></i> Cat Detected</span>' :
                '<span class="text-muted">No cat present</span>';
            document.getElementById('system-status').innerHTML = data.running ?
                '<span class="text-success">Running</span>' :
                '<span class="text-danger">Stopped</span>';
        })
        .catch(error => console.error('Error updating status:', error));
}

function feedCat(portion) {
    fetch('/api/feed', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({portion: portion})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Feeding started!', 'success');
            updateStatus();
        } else {
            showAlert('Feeding failed: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Feeding failed', 'danger');
    });
}

function tareScale() {
    fetch('/api/tare', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Scale tared successfully!', 'success');
            updateStatus();
        } else {
            showAlert('Tare failed: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Tare failed', 'danger');
    });
}

function toggleSchedule(index, enabled) {
    fetch('/api/schedules')
    .then(response => response.json())
    .then(schedules => {
        schedules[index].enabled = enabled;
        return fetch('/api/schedules', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(schedules)
        });
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Schedule updated!', 'success');
        } else {
            showAlert('Update failed: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Update failed', 'danger');
    });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
</script>
{% endblock %}'''
        
        # Write templates to files
        with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
            f.write(base_template)
        
        with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
            f.write(index_template)
    
    def start(self, host='0.0.0.0', port=5000):
        """Start the web server"""
        try:
            logger.info(f"Starting web interface on {host}:{port}")
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
    
    def stop(self):
        """Stop the web server"""
        logger.info("Stopping web interface")
        # Flask doesn't have a built-in stop method, but the server will stop
        # when the main thread exits 