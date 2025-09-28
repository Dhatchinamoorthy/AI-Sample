from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.banking.base import BaseBankingWidget


class OffersWidget(BaseBankingWidget):
    """Banking offers widget implementation"""
    
    def get_widget_type(self) -> str:
        return "banking_offers"
    
    def get_default_config(self) -> Dict[str, Any]:
        base_config = super().get_banking_config()
        base_config.update({
            "size": "medium",
            "theme": "banking",
            "show_offer_details": True,
            "show_validity": True,
            "show_requirements": True,
            "group_by_category": True,
            "sort_by": "valid_until",  # valid_until, value, category
            "limit": 10
        })
        return base_config
    
    def create_widget_data(self, offers_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create offers widget data"""
        try:
            formatted_data = self.format_data(offers_data)
            
            widget_data = {
                "id": f"offers_{int(datetime.now().timestamp())}",
                "type": "banking_offers",
                "title": "Available Offers",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "banking_api" if not offers_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create offers widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format offers data for display"""
        try:
            offers = raw_data.get("offers", [])
            
            # Group offers by category
            offers_by_category = {}
            for offer in offers:
                category = offer.get("category", "other")
                if category not in offers_by_category:
                    offers_by_category[category] = []
                offers_by_category[category].append(offer)
            
            # Format each offer
            formatted_offers = []
            for offer in offers:
                valid_until = offer.get("valid_until", "")
                is_expired = self._is_offer_expired(valid_until)
                days_remaining = self._get_days_remaining(valid_until)
                
                formatted_offer = {
                    "id": offer.get("id", ""),
                    "title": offer.get("title", ""),
                    "description": offer.get("description", ""),
                    "category": offer.get("category", ""),
                    "type": offer.get("type", ""),
                    "value": offer.get("value", ""),
                    "valid_until": valid_until,
                    "valid_until_formatted": self.format_date(valid_until),
                    "requirements": offer.get("requirements", ""),
                    "status": offer.get("status", ""),
                    "is_expired": is_expired,
                    "days_remaining": days_remaining,
                    "priority": self._get_offer_priority(offer)
                }
                formatted_offers.append(formatted_offer)
            
            # Sort by priority and validity
            formatted_offers.sort(key=lambda x: (x["is_expired"], -x["priority"], x["valid_until"]))
            
            return {
                "offers": formatted_offers,
                "offers_by_category": offers_by_category,
                "summary": {
                    "total_offers": len(offers),
                    "active_offers": len([o for o in formatted_offers if not o["is_expired"]]),
                    "expired_offers": len([o for o in formatted_offers if o["is_expired"]]),
                    "categories": list(offers_by_category.keys())
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _is_offer_expired(self, valid_until: str) -> bool:
        """Check if offer is expired"""
        try:
            if not valid_until:
                return False
            expiry_date = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
            return datetime.now(timezone.utc) > expiry_date
        except:
            return False
    
    def _get_days_remaining(self, valid_until: str) -> int:
        """Get days remaining for offer"""
        try:
            if not valid_until:
                return 0
            expiry_date = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            delta = expiry_date - now
            return max(0, delta.days)
        except:
            return 0
    
    def _get_offer_priority(self, offer: Dict[str, Any]) -> int:
        """Calculate offer priority based on value and type"""
        priority = 0
        
        # Higher priority for bonus offers
        if offer.get("type") == "bonus":
            priority += 3
        
        # Higher priority for cashback offers
        elif offer.get("type") == "cashback":
            priority += 2
        
        # Higher priority for rate reductions
        elif offer.get("type") == "rate_reduction":
            priority += 1
        
        # Check value for additional priority
        value = offer.get("value", "")
        if "$" in value:
            try:
                # Extract numeric value
                numeric_value = float(value.replace("$", "").replace(",", ""))
                if numeric_value > 100:
                    priority += 2
                elif numeric_value > 50:
                    priority += 1
            except:
                pass
        
        return priority
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate offers widget configuration"""
        required_fields = ["size", "theme", "limit"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate limit
        if not isinstance(config["limit"], int) or config["limit"] < 1 or config["limit"] > 50:
            return False
        
        # Validate sort options
        if "sort_by" in config:
            if config["sort_by"] not in ["valid_until", "value", "category"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["offers", "total_count"]
    
    def get_optional_fields(self) -> List[str]:
        return ["categories", "summary", "offers_by_category"]
    
    def get_display_template(self) -> str:
        return "banking_offers"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        actions = super().get_banking_actions()
        actions.extend([
            {
                "type": "filter",
                "label": "Filter Offers",
                "icon": "filter_list",
                "description": "Filter by category or type"
            },
            {
                "type": "apply",
                "label": "Apply Offer",
                "icon": "check_circle",
                "description": "Apply for selected offer"
            },
            {
                "type": "remind",
                "label": "Set Reminder",
                "icon": "alarm",
                "description": "Set reminder for offer expiry"
            }
        ])
        return actions
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"offers_error_{int(datetime.now().timestamp())}",
            "type": "banking_offers",
            "title": "Offers Widget Error",
            "data": {
                "error": error_message,
                "offers": [],
                "summary": {
                    "total_offers": 0,
                    "active_offers": 0,
                    "expired_offers": 0,
                    "categories": []
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
