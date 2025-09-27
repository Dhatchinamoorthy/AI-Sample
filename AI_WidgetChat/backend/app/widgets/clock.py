from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class ClockWidget(BaseWidget):
    """Clock widget implementation"""
    
    def get_widget_type(self) -> str:
        return "clock"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "size": "small",
            "theme": "auto",
            "refreshInterval": 30,  # 30 seconds
            "showDate": True,
            "showSeconds": True,
            "format24Hour": False,
            "showTimezone": True,
            "showDayOfWeek": True
        }
    
    def create_widget_data(self, timezone: str, location: Optional[str], time_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create clock widget data"""
        try:
            # Format the time data
            formatted_data = self.format_data(time_data)
            
            # Create widget protocol
            widget_data = {
                "id": f"clock_{timezone.lower().replace('/', '_')}_{int(datetime.now().timestamp())}",
                "type": "clock",
                "title": f"Clock - {location or timezone}",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().astimezone().isoformat(),
                    "updated_at": datetime.now().astimezone().isoformat(),
                    "source": "system" if not time_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create clock widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format time data for display"""
        try:
            current_time = raw_data.get("current_time", "")
            time_12h = raw_data.get("time_12h", "")
            date = raw_data.get("date", "")
            
            # Parse the current time to extract components
            time_parts = current_time.split(" ")
            time_part = time_parts[0] if time_parts else current_time
            date_part = time_parts[1] if len(time_parts) > 1 else date
            
            # Extract time components
            time_components = time_part.split(":")
            hour = int(time_components[0]) if len(time_components) > 0 else 0
            minute = int(time_components[1]) if len(time_components) > 1 else 0
            second = int(time_components[2]) if len(time_components) > 2 else 0
            
            # Determine if it's AM or PM
            is_am = hour < 12
            am_pm = "AM" if is_am else "PM"
            
            # Format hour for 12-hour display
            hour_12 = hour if hour <= 12 else hour - 12
            if hour_12 == 0:
                hour_12 = 12
            
            return {
                "timezone": raw_data.get("timezone", "UTC"),
                "location": raw_data.get("location", "Unknown"),
                "time": {
                    "current": current_time,
                    "formatted_12h": time_12h,
                    "formatted_24h": current_time,
                    "hour": hour,
                    "hour_12": hour_12,
                    "minute": minute,
                    "second": second,
                    "am_pm": am_pm
                },
                "date": {
                    "full": date,
                    "day_of_week": self._extract_day_of_week(date),
                    "month": self._extract_month(date),
                    "day": self._extract_day(date),
                    "year": self._extract_year(date)
                },
                "utc_offset": raw_data.get("utc_offset", "+0000"),
                "timestamp": raw_data.get("timestamp", datetime.now().astimezone().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_day_of_week(self, date_str: str) -> str:
        """Extract day of week from date string"""
        try:
            # Common day names
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days:
                if day.lower() in date_str.lower():
                    return day
            return "Unknown"
        except:
            return "Unknown"
    
    def _extract_month(self, date_str: str) -> str:
        """Extract month from date string"""
        try:
            # Common month names
            months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            for month in months:
                if month.lower() in date_str.lower():
                    return month
            return "Unknown"
        except:
            return "Unknown"
    
    def _extract_day(self, date_str: str) -> str:
        """Extract day from date string"""
        try:
            import re
            # Look for day number
            day_match = re.search(r'\b(\d{1,2})\b', date_str)
            if day_match:
                return day_match.group(1)
            return "Unknown"
        except:
            return "Unknown"
    
    def _extract_year(self, date_str: str) -> str:
        """Extract year from date string"""
        try:
            import re
            # Look for 4-digit year
            year_match = re.search(r'\b(\d{4})\b', date_str)
            if year_match:
                return year_match.group(1)
            return "Unknown"
        except:
            return "Unknown"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate clock widget configuration"""
        required_fields = ["size", "theme"]
        optional_fields = ["refreshInterval", "showDate", "showSeconds", "format24Hour", "showTimezone", "showDayOfWeek"]
        
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
        
        # Validate refresh interval (should be reasonable for clock)
        if "refreshInterval" in config:
            if not isinstance(config["refreshInterval"], int) or config["refreshInterval"] < 1 or config["refreshInterval"] > 3600:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["current_time", "timezone"]
    
    def get_optional_fields(self) -> List[str]:
        return ["date", "utc_offset", "location"]
    
    def get_display_template(self) -> str:
        return "clock"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            self.create_action("refresh"),
            self.create_action("configure"),
            {
                "type": "timezone",
                "label": "Change Timezone",
                "icon": "schedule",
                "description": "Change the timezone"
            },
            {
                "type": "world_clock",
                "label": "World Clock",
                "icon": "public",
                "description": "View multiple timezones"
            }
        ]
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"clock_error_{int(datetime.now().timestamp())}",
            "type": "clock",
            "title": "Clock Widget Error",
            "data": {
                "error": error_message,
                "timezone": "UTC",
                "location": "Unknown",
                "time": {
                    "current": "00:00:00",
                    "formatted_12h": "12:00:00 AM",
                    "formatted_24h": "00:00:00",
                    "hour": 0,
                    "hour_12": 12,
                    "minute": 0,
                    "second": 0,
                    "am_pm": "AM"
                },
                "date": {
                    "full": "Unknown Date",
                    "day_of_week": "Unknown",
                    "month": "Unknown",
                    "day": "Unknown",
                    "year": "Unknown"
                },
                "utc_offset": "+0000",
                "timestamp": datetime.now().astimezone().isoformat()
            },
            "config": self.default_config,
            "actions": [self.create_action("refresh")],
            "metadata": {
                "created_at": datetime.now().astimezone().isoformat(),
                "updated_at": datetime.now().astimezone().isoformat(),
                "source": "error",
                "version": "1.0.0"
            }
        }
