"""
Intelligent Fire Detection, Smoke Monitoring, and Emergency Warning System
Main Module: Real-Time Fire Hazard Detection and Emergency Alert Management

This module implements a comprehensive fire safety system that simulates
real-time environmental monitoring, fire detection, and emergency response.

Author: Internship Project Team
Date: 2024
"""

import json
import random
import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Fire alert severity levels"""
    NORMAL = "Normal"
    WARNING = "Warning"
    ALERT = "Alert"
    CRITICAL = "Critical"
    EMERGENCY = "Emergency"


class SensorType(Enum):
    """Types of fire detection sensors"""
    FLAME = "Flame Sensor"
    SMOKE = "Smoke Sensor"
    TEMPERATURE = "Temperature Sensor"
    CO = "Carbon Monoxide Sensor"
    HUMIDITY = "Humidity Sensor"


class LocationZone(Enum):
    """Building zones for fire detection"""
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    WAREHOUSE = "Warehouse"
    HOSPITAL = "Hospital"


@dataclass
class SensorReading:
    """Data class representing a sensor reading"""
    sensor_id: str
    timestamp: datetime.datetime
    sensor_type: SensorType
    zone: LocationZone
    value: float
    unit: str
    status: str
    alert_level: AlertLevel
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'sensor_type': self.sensor_type.value,
            'zone': self.zone.value,
            'value': round(self.value, 2),
            'unit': self.unit,
            'status': self.status,
            'alert_level': self.alert_level.value
        }


@dataclass
class FireAlert:
    """Data class representing a fire alert"""
    alert_id: str
    zone: LocationZone
    alert_type: str  # 'SMOKE_DETECTED', 'HIGH_TEMPERATURE', 'FLAME_DETECTED', 'CO_DETECTED'
    alert_level: AlertLevel
    message: str
    timestamp: datetime.datetime
    sensors_triggered: List[str]
    emergency_services_notified: bool = False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'zone': self.zone.value,
            'alert_type': self.alert_type,
            'alert_level': self.alert_level.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'sensors_triggered': self.sensors_triggered,
            'emergency_services_notified': self.emergency_services_notified
        }


@dataclass
class EvacuationEvent:
    """Data class representing an evacuation event"""
    event_id: str
    zone: LocationZone
    trigger_time: datetime.datetime
    alert_id: str
    occupants_alerted: int
    evacuation_status: str  # 'INITIATED', 'IN_PROGRESS', 'COMPLETED'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'zone': self.zone.value,
            'trigger_time': self.trigger_time.isoformat(),
            'alert_id': self.alert_id,
            'occupants_alerted': self.occupants_alerted,
            'evacuation_status': self.evacuation_status
        }


class FireSensor:
    """Class representing a fire detection sensor"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType, zone: LocationZone):
        """
        Initialize a fire detection sensor
        
        Args:
            sensor_id: Unique sensor identifier
            sensor_type: Type of sensor
            zone: Building zone where sensor is installed
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.zone = zone
        self.readings: List[SensorReading] = []
        self.battery_level = 100.0
        self.last_reading: Optional[SensorReading] = None
        self.is_functional = True
        self.calibration_needed = False
        self.reading_count = 0
        
        # Set sensor-specific thresholds
        self._set_thresholds()
    
    def _set_thresholds(self):
        """Set alert thresholds based on sensor type"""
        if self.sensor_type == SensorType.FLAME:
            self.normal_threshold = 0.1
            self.warning_threshold = 0.3
            self.alert_threshold = 0.6
            self.critical_threshold = 0.8
        elif self.sensor_type == SensorType.SMOKE:
            self.normal_threshold = 50  # ppm
            self.warning_threshold = 100
            self.alert_threshold = 200
            self.critical_threshold = 400
        elif self.sensor_type == SensorType.TEMPERATURE:
            self.normal_threshold = 30  # Celsius
            self.warning_threshold = 50
            self.alert_threshold = 70
            self.critical_threshold = 100
        elif self.sensor_type == SensorType.CO:
            self.normal_threshold = 10  # ppm
            self.warning_threshold = 35
            self.alert_threshold = 100
            self.critical_threshold = 1200
        else:  # HUMIDITY
            self.normal_threshold = 30
            self.warning_threshold = 20
            self.alert_threshold = 10
            self.critical_threshold = 5
    
    def take_reading(self, environmental_factor: float = 1.0) -> SensorReading:
        """
        Take a sensor reading
        
        Args:
            environmental_factor: Factor representing fire conditions (0.0 = normal, 1.0 = severe fire)
            
        Returns:
            SensorReading object
        """
        timestamp = datetime.datetime.now()
        
        # Generate sensor value based on environmental conditions
        if self.sensor_type == SensorType.FLAME:
            base_value = random.uniform(0.05, 0.15)
            value = base_value + (environmental_factor * random.uniform(0.5, 1.0))
            unit = "Intensity (0-1)"
        elif self.sensor_type == SensorType.SMOKE:
            base_value = random.uniform(30, 60)
            value = base_value + (environmental_factor * random.uniform(100, 400))
            unit = "ppm"
        elif self.sensor_type == SensorType.TEMPERATURE:
            base_value = random.uniform(20, 30)
            value = base_value + (environmental_factor * random.uniform(30, 80))
            unit = "°C"
        elif self.sensor_type == SensorType.CO:
            base_value = random.uniform(5, 15)
            value = base_value + (environmental_factor * random.uniform(50, 200))
            unit = "ppm"
        else:  # HUMIDITY
            base_value = random.uniform(40, 60)
            value = base_value - (environmental_factor * random.uniform(10, 30))
            unit = "%"
        
        # Add sensor noise
        value += random.uniform(-5, 5)
        value = max(0, value)
        
        # Determine alert level
        if value <= self.normal_threshold:
            alert_level = AlertLevel.NORMAL
            status = "Normal"
        elif value <= self.warning_threshold:
            alert_level = AlertLevel.WARNING
            status = "Warning"
        elif value <= self.alert_threshold:
            alert_level = AlertLevel.ALERT
            status = "Alert"
        elif value <= self.critical_threshold:
            alert_level = AlertLevel.CRITICAL
            status = "Critical"
        else:
            alert_level = AlertLevel.EMERGENCY
            status = "Emergency"
        
        # Create reading
        reading = SensorReading(
            sensor_id=self.sensor_id,
            timestamp=timestamp,
            sensor_type=self.sensor_type,
            zone=self.zone,
            value=value,
            unit=unit,
            status=status,
            alert_level=alert_level
        )
        
        self.readings.append(reading)
        self.last_reading = reading
        self.reading_count += 1
        
        # Update battery
        self.battery_level -= random.uniform(0.05, 0.15)
        
        return reading
    
    def get_sensor_status(self) -> Dict:
        """Get current sensor status"""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.value,
            'zone': self.zone.value,
            'is_functional': self.is_functional,
            'battery_level': round(self.battery_level, 2),
            'calibration_needed': self.calibration_needed,
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'total_readings': self.reading_count
        }


class FireDetectionZone:
    """Class representing a monitored zone with multiple sensors"""
    
    def __init__(self, zone: LocationZone, occupancy: int = 50):
        """
        Initialize a fire detection zone
        
        Args:
            zone: Type of zone
            occupancy: Number of occupants in the zone
        """
        self.zone = zone
        self.occupancy = occupancy
        self.sensors: Dict[str, FireSensor] = {}
        self.alerts: List[FireAlert] = []
        self.evacuation_events: List[EvacuationEvent] = []
        self.fire_detected = False
        self.alarm_activated = False
        self.sprinkler_activated = False
        
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize sensors for the zone"""
        sensor_configs = [
            (SensorType.FLAME, 1),
            (SensorType.SMOKE, 2),
            (SensorType.TEMPERATURE, 2),
            (SensorType.CO, 1),
            (SensorType.HUMIDITY, 1)
        ]
        
        sensor_count = 1
        for sensor_type, count in sensor_configs:
            for i in range(count):
                sensor_id = f"SENSOR_{self.zone.value}_{sensor_type.value.replace(' ', '_')}_{i+1}"
                sensor = FireSensor(sensor_id, sensor_type, self.zone)
                self.sensors[sensor_id] = sensor
                sensor_count += 1
    
    def monitor_zone(self, environmental_factor: float = 0.0):
        """
        Monitor the zone by reading all sensors
        
        Args:
            environmental_factor: Fire condition factor (0.0 = normal, 1.0 = severe fire)
        """
        readings = []
        critical_count = 0
        alert_count = 0
        
        for sensor_id, sensor in self.sensors.items():
            reading = sensor.take_reading(environmental_factor)
            readings.append(reading)
            
            if reading.alert_level == AlertLevel.CRITICAL:
                critical_count += 1
            elif reading.alert_level == AlertLevel.ALERT:
                alert_count += 1
        
        # Determine if fire should be detected
        if critical_count >= 2 or (alert_count >= 3 and critical_count >= 1):
            self.fire_detected = True
            self._generate_fire_alert(readings)
        elif alert_count >= 4:
            self._generate_fire_alert(readings)
        
        # Activate sprinkler if fire is detected
        if self.fire_detected and not self.sprinkler_activated:
            self.sprinkler_activated = True
            logger.info(f"Sprinkler system activated in {self.zone.value} zone")
    
    def _generate_fire_alert(self, readings: List[SensorReading]):
        """Generate a fire alert based on sensor readings"""
        timestamp = datetime.datetime.now()
        alert_id = f"ALERT_{len(self.alerts) + 1}"
        
        # Determine alert type based on sensor readings
        alert_type = "FIRE_DETECTED"
        max_alert_level = AlertLevel.NORMAL
        triggered_sensors = []
        
        for reading in readings:
            if reading.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                triggered_sensors.append(reading.sensor_id)
                if reading.alert_level.value > max_alert_level.value:
                    max_alert_level = reading.alert_level
                
                if reading.sensor_type == SensorType.SMOKE:
                    alert_type = "SMOKE_DETECTED"
                elif reading.sensor_type == SensorType.FLAME:
                    alert_type = "FLAME_DETECTED"
                elif reading.sensor_type == SensorType.TEMPERATURE:
                    alert_type = "HIGH_TEMPERATURE"
                elif reading.sensor_type == SensorType.CO:
                    alert_type = "CO_DETECTED"
        
        # Create alert
        alert = FireAlert(
            alert_id=alert_id,
            zone=self.zone,
            alert_type=alert_type,
            alert_level=max_alert_level,
            message=f"Fire hazard detected in {self.zone.value} zone - {alert_type}",
            timestamp=timestamp,
            sensors_triggered=triggered_sensors,
            emergency_services_notified=True
        )
        
        self.alerts.append(alert)
        self.alarm_activated = True
        
        # Trigger evacuation
        self._initiate_evacuation(alert)
        
        logger.critical(f"{alert_type} in {self.zone.value}: {alert.message}")
    
    def _initiate_evacuation(self, alert: FireAlert):
        """Initiate evacuation procedures"""
        event_id = f"EVAC_{len(self.evacuation_events) + 1}"
        
        event = EvacuationEvent(
            event_id=event_id,
            zone=self.zone,
            trigger_time=alert.timestamp,
            alert_id=alert.alert_id,
            occupants_alerted=self.occupancy,
            evacuation_status="INITIATED"
        )
        
        self.evacuation_events.append(event)
        logger.warning(f"Evacuation initiated for {self.zone.value}: {self.occupancy} occupants alerted")
    
    def get_zone_status(self) -> Dict:
        """Get current zone status"""
        return {
            'zone': self.zone.value,
            'occupancy': self.occupancy,
            'fire_detected': self.fire_detected,
            'alarm_activated': self.alarm_activated,
            'sprinkler_activated': self.sprinkler_activated,
            'total_sensors': len(self.sensors),
            'total_alerts': len(self.alerts),
            'active_alerts': len([a for a in self.alerts if a.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]),
            'evacuation_events': len(self.evacuation_events)
        }


class FireDetectionSystem:
    """Central fire detection and emergency warning system"""
    
    def __init__(self):
        """Initialize the fire detection system"""
        self.zones: Dict[LocationZone, FireDetectionZone] = {}
        self.all_readings: List[SensorReading] = []
        self.all_alerts: List[FireAlert] = []
        self.all_evacuations: List[EvacuationEvent] = []
        self.operation_log: List[Dict] = []
        
        self._initialize_zones()
        logger.info("Fire Detection System initialized")
    
    def _initialize_zones(self):
        """Initialize monitoring zones"""
        zone_configs = [
            (LocationZone.RESIDENTIAL, 30),
            (LocationZone.COMMERCIAL, 100),
            (LocationZone.INDUSTRIAL, 150),
            (LocationZone.WAREHOUSE, 80),
            (LocationZone.HOSPITAL, 200)
        ]
        
        for zone, occupancy in zone_configs:
            zone_obj = FireDetectionZone(zone, occupancy)
            self.zones[zone] = zone_obj
    
    def simulate_monitoring_cycle(self, environmental_factors: Dict[LocationZone, float]):
        """
        Simulate one monitoring cycle across all zones
        
        Args:
            environmental_factors: Fire condition factors for each zone
        """
        for zone, factor in environmental_factors.items():
            zone_obj = self.zones[zone]
            zone_obj.monitor_zone(factor)
            
            # Collect readings and alerts
            for sensor in zone_obj.sensors.values():
                if sensor.last_reading:
                    self.all_readings.append(sensor.last_reading)
            
            for alert in zone_obj.alerts:
                if alert not in self.all_alerts:
                    self.all_alerts.append(alert)
            
            for evacuation in zone_obj.evacuation_events:
                if evacuation not in self.all_evacuations:
                    self.all_evacuations.append(evacuation)
    
    def simulate_24_hour_cycle(self):
        """Simulate a 24-hour fire detection cycle"""
        logger.info("Starting 24-hour fire detection simulation")
        
        for hour in range(24):
            # Simulate varying fire risk throughout the day
            environmental_factors = {}
            
            for zone in self.zones.keys():
                # Higher fire risk during peak hours (8-18)
                if 8 <= hour <= 18:
                    base_factor = random.uniform(0.0, 0.2)
                else:
                    base_factor = random.uniform(0.0, 0.1)
                
                # Occasional fire incident
                if random.random() < 0.05:  # 5% chance of fire
                    base_factor = random.uniform(0.5, 1.0)
                
                environmental_factors[zone] = base_factor
            
            self.simulate_monitoring_cycle(environmental_factors)
            
            # Log hourly status
            self.operation_log.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'hour': hour,
                'total_alerts': len(self.all_alerts),
                'fires_detected': len([z for z in self.zones.values() if z.fire_detected]),
                'evacuations': len(self.all_evacuations)
            })
            
            logger.info(f"Hour {hour:02d}:00 - Alerts: {len(self.all_alerts)}, "
                       f"Fires: {len([z for z in self.zones.values() if z.fire_detected])}")
        
        logger.info("24-hour simulation completed")
    
    def get_system_statistics(self) -> Dict:
        """Get system-wide statistics"""
        total_zones = len(self.zones)
        zones_with_fire = len([z for z in self.zones.values() if z.fire_detected])
        total_sensors = sum(len(z.sensors) for z in self.zones.values())
        
        # Count alert types
        alert_distribution = {}
        for alert in self.all_alerts:
            alert_distribution[alert.alert_type] = alert_distribution.get(alert.alert_type, 0) + 1
        
        return {
            'total_zones': total_zones,
            'zones_with_fire': zones_with_fire,
            'total_sensors': total_sensors,
            'total_readings': len(self.all_readings),
            'total_alerts': len(self.all_alerts),
            'critical_alerts': len([a for a in self.all_alerts if a.alert_level == AlertLevel.CRITICAL]),
            'emergency_alerts': len([a for a in self.all_alerts if a.alert_level == AlertLevel.EMERGENCY]),
            'total_evacuations': len(self.all_evacuations),
            'alert_distribution': alert_distribution
        }
    
    def export_to_json(self, filename: str):
        """Export system data to JSON"""
        data = {
            'system_name': 'Intelligent Fire Detection System',
            'total_zones': len(self.zones),
            'zones': {zone.value: zone_obj.get_zone_status() for zone, zone_obj in self.zones.items()},
            'statistics': self.get_system_statistics(),
            'alerts': [alert.to_dict() for alert in self.all_alerts[-50:]],  # Last 50 alerts
            'evacuations': [evac.to_dict() for evac in self.all_evacuations],
            'operation_log': self.operation_log
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")


if __name__ == "__main__":
    # Create fire detection system
    system = FireDetectionSystem()
    
    # Run simulation
    system.simulate_24_hour_cycle()
    
    # Get statistics
    stats = system.get_system_statistics()
    
    # Print report
    print("\n" + "="*60)
    print("FIRE DETECTION SYSTEM - SIMULATION REPORT")
    print("="*60)
    print(json.dumps(stats, indent=2))
    
    # Export data
    system.export_to_json('/home/ubuntu/fire_detection_system_data.json')
