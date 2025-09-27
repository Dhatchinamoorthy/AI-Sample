from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseWidget(ABC):
    """Base class for all widgets"""
    
    def __init__(self):
        self.widget_type = self.get_widget_type()
        self.default_config = self.get_default_config()
    
    @abstractmethod
    def get_widget_type(self) -> str:
        """Return the widget type identifier"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration for the widget"""
        pass
    
    @abstractmethod
    def create_widget_data(self, *args, **kwargs) -> Dict[str, Any]:
        """Create widget data from external data source"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate widget configuration"""
        pass
    
    def get_required_fields(self) -> List[str]:
        """Return list of required fields for the widget"""
        return []
    
    def get_optional_fields(self) -> List[str]:
        """Return list of optional fields for the widget"""
        return []
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw data for widget display"""
        return raw_data
    
    def get_display_template(self) -> str:
        """Return the display template for the widget"""
        return "default"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        """Return list of supported actions for the widget"""
        return []
    
    def create_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """Create an action for the widget"""
        actions = {
            "refresh": {
                "type": "refresh",
                "label": "Refresh",
                "icon": "refresh",
                "description": "Refresh widget data"
            },
            "configure": {
                "type": "configure",
                "label": "Configure",
                "icon": "settings",
                "description": "Configure widget settings"
            },
            "fullscreen": {
                "type": "fullscreen",
                "label": "Fullscreen",
                "icon": "fullscreen",
                "description": "View in fullscreen"
            }
        }
        
        action = actions.get(action_type, {})
        action.update(kwargs)
        return action
    
    def get_widget_size_options(self) -> List[str]:
        """Return available size options for the widget"""
        return ["small", "medium", "large"]
    
    def get_theme_options(self) -> List[str]:
        """Return available theme options for the widget"""
        return ["light", "dark", "auto"]
    
    def should_show_timestamp(self) -> bool:
        """Determine if widget should show timestamp"""
        return True
    
    def get_error_message(self, error: str) -> str:
        """Return formatted error message for the widget"""
        return f"Error loading {self.widget_type} widget: {error}"
