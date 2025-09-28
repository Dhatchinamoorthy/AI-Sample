from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.banking.base import BaseBankingWidget


class BankerWidget(BaseBankingWidget):
    """Banking banker contacts widget implementation"""
    
    def get_widget_type(self) -> str:
        return "banking_banker"
    
    def get_default_config(self) -> Dict[str, Any]:
        base_config = super().get_banking_config()
        base_config.update({
            "size": "medium",
            "theme": "banking",
            "show_contact_info": True,
            "show_availability": True,
            "show_specialization": True,
            "group_by_department": True,
            "sort_by": "experience",  # experience, name, department
            "show_languages": True
        })
        return base_config
    
    def create_widget_data(self, banker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create banker widget data"""
        try:
            formatted_data = self.format_data(banker_data)
            
            widget_data = {
                "id": f"banker_{int(datetime.now().timestamp())}",
                "type": "banking_banker",
                "title": "Banker Contacts",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "banking_api" if not banker_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create banker widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format banker data for display"""
        try:
            bankers = raw_data.get("bankers", [])
            
            # Group bankers by department
            bankers_by_department = {}
            for banker in bankers:
                department = banker.get("department", "other")
                if department not in bankers_by_department:
                    bankers_by_department[department] = []
                bankers_by_department[department].append(banker)
            
            # Format each banker
            formatted_bankers = []
            for banker in bankers:
                experience_years = self._extract_experience_years(banker.get("experience", "0 years"))
                is_available = self._is_banker_available(banker.get("availability", ""))
                
                formatted_banker = {
                    "id": banker.get("id", ""),
                    "name": banker.get("name", ""),
                    "title": banker.get("title", ""),
                    "department": banker.get("department", ""),
                    "specialization": banker.get("specialization", ""),
                    "email": banker.get("email", ""),
                    "phone": banker.get("phone", ""),
                    "availability": banker.get("availability", ""),
                    "experience": banker.get("experience", ""),
                    "experience_years": experience_years,
                    "languages": banker.get("languages", []),
                    "is_available": is_available,
                    "contact_methods": self._get_contact_methods(banker),
                    "expertise_level": self._get_expertise_level(experience_years)
                }
                formatted_bankers.append(formatted_banker)
            
            # Sort by availability and experience
            formatted_bankers.sort(key=lambda x: (not x["is_available"], -x["experience_years"]))
            
            return {
                "bankers": formatted_bankers,
                "bankers_by_department": bankers_by_department,
                "summary": {
                    "total_bankers": len(bankers),
                    "available_bankers": len([b for b in formatted_bankers if b["is_available"]]),
                    "departments": list(bankers_by_department.keys()),
                    "specializations": list(set(b["specialization"] for b in bankers if b["specialization"]))
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_experience_years(self, experience_str: str) -> int:
        """Extract years of experience from string"""
        try:
            import re
            match = re.search(r'(\d+)', experience_str)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def _is_banker_available(self, availability: str) -> bool:
        """Check if banker is currently available"""
        try:
            if not availability:
                return False
            
            # Simple check for current time availability
            now = datetime.now()
            current_hour = now.hour
            current_weekday = now.weekday()  # 0 = Monday, 6 = Sunday
            
            # Check if it's a weekday and within business hours
            if "Mon-Fri" in availability and current_weekday < 5:
                if "9AM-5PM" in availability and 9 <= current_hour < 17:
                    return True
                elif "8AM-6PM" in availability and 8 <= current_hour < 18:
                    return True
            
            return False
        except:
            return False
    
    def _get_contact_methods(self, banker: Dict[str, Any]) -> List[str]:
        """Get available contact methods for banker"""
        methods = []
        if banker.get("email"):
            methods.append("email")
        if banker.get("phone"):
            methods.append("phone")
        return methods
    
    def _get_expertise_level(self, experience_years: int) -> str:
        """Determine expertise level based on experience"""
        if experience_years >= 10:
            return "expert"
        elif experience_years >= 5:
            return "senior"
        elif experience_years >= 2:
            return "intermediate"
        else:
            return "junior"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate banker widget configuration"""
        required_fields = ["size", "theme"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate sort options
        if "sort_by" in config:
            if config["sort_by"] not in ["experience", "name", "department"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["bankers", "total_count"]
    
    def get_optional_fields(self) -> List[str]:
        return ["departments", "specializations", "summary", "bankers_by_department"]
    
    def get_display_template(self) -> str:
        return "banking_banker"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        actions = super().get_banking_actions()
        actions.extend([
            {
                "type": "contact",
                "label": "Contact Banker",
                "icon": "phone",
                "description": "Contact selected banker"
            },
            {
                "type": "schedule",
                "label": "Schedule Meeting",
                "icon": "event",
                "description": "Schedule appointment with banker"
            },
            {
                "type": "filter",
                "label": "Filter by Department",
                "icon": "filter_list",
                "description": "Filter bankers by department"
            },
            {
                "type": "search",
                "label": "Search Bankers",
                "icon": "search",
                "description": "Search for specific banker"
            }
        ])
        return actions
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"banker_error_{int(datetime.now().timestamp())}",
            "type": "banking_banker",
            "title": "Banker Widget Error",
            "data": {
                "error": error_message,
                "bankers": [],
                "summary": {
                    "total_bankers": 0,
                    "available_bankers": 0,
                    "departments": [],
                    "specializations": []
                },
                "timestamp": datetime.now().isoformat()
            },
            "config": self.default_config,
            "actions": [{"type": "refresh", "label": "Retry", "icon": "refresh"}],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "error",
                "version": "1.0.0"
            }
        }
