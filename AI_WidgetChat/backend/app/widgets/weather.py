from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class WeatherWidget(BaseWidget):
    """Weather widget implementation"""
    
    def get_widget_type(self) -> str:
        return "weather"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "size": "medium",
            "theme": "auto",
            "refreshInterval": 300,  # 5 minutes
            "showDetails": True,
            "showForecast": False,
            "temperatureUnit": "celsius",  # celsius or fahrenheit
            "showWind": True,
            "showHumidity": True
        }
    
    def create_widget_data(self, location: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create weather widget data"""
        try:
            # Format the weather data
            formatted_data = self.format_data(weather_data)
            
            # Create widget protocol
            widget_data = {
                "id": f"weather_{location.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}",
                "type": "weather",
                "title": f"Weather in {location}",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "openweathermap" if not weather_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create weather widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format weather data for display"""
        try:
            return {
                "location": {
                    "name": raw_data.get("location", "Unknown"),
                    "country": raw_data.get("country", "")
                },
                "current": {
                    "temperature": raw_data.get("temperature", 0),
                    "feels_like": raw_data.get("feels_like", 0),
                    "description": raw_data.get("description", "Unknown"),
                    "icon": raw_data.get("icon", "01d")
                },
                "details": {
                    "humidity": raw_data.get("humidity", 0),
                    "pressure": raw_data.get("pressure", 0),
                    "wind_speed": raw_data.get("wind_speed", 0),
                    "visibility": raw_data.get("visibility", 0)
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate weather widget configuration"""
        required_fields = ["size", "theme"]
        optional_fields = ["refreshInterval", "showDetails", "showForecast", "temperatureUnit", "showWind", "showHumidity"]
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate size
        if config["size"] not in self.get_widget_size_options():
            return False
        
        # Validate theme
        if config["theme"] not in self.get_theme_options():
            return False
        
        # Validate temperature unit
        if "temperatureUnit" in config:
            if config["temperatureUnit"] not in ["celsius", "fahrenheit"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["location", "temperature", "description"]
    
    def get_optional_fields(self) -> List[str]:
        return ["humidity", "pressure", "wind_speed", "visibility", "feels_like", "icon"]
    
    def get_display_template(self) -> str:
        return "weather"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            self.create_action("refresh"),
            self.create_action("configure"),
            {
                "type": "forecast",
                "label": "7-Day Forecast",
                "icon": "calendar",
                "description": "View 7-day weather forecast"
            }
        ]
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"weather_error_{int(datetime.now().timestamp())}",
            "type": "weather",
            "title": "Weather Widget Error",
            "data": {
                "error": error_message,
                "location": {"name": "Unknown", "country": ""},
                "current": {
                    "temperature": 0,
                    "feels_like": 0,
                    "description": "Unable to load weather data",
                    "icon": "error"
                },
                "details": {
                    "humidity": 0,
                    "pressure": 0,
                    "wind_speed": 0,
                    "visibility": 0
                },
                "timestamp": datetime.now().isoformat()
            },
            "config": self.default_config,
            "actions": [self.create_action("refresh")],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "error",
                "version": "1.0.0"
            }
        }
