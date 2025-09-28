from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class BaseBankingWidget(BaseWidget):
    """Base class for all banking widgets"""
    
    def get_banking_config(self) -> Dict[str, Any]:
        """Return banking-specific configuration"""
        return {
            "show_balance": True,
            "show_last_activity": True,
            "show_status": True,
            "refresh_interval": 300,  # 5 minutes
            "security_level": "high"
        }
    
    def format_currency(self, amount: float, currency: str = "USD") -> str:
        """Format currency amount for display"""
        if currency == "USD":
            return f"${amount:,.2f}"
        return f"{amount:,.2f} {currency}"
    
    def format_date(self, date_str: str) -> str:
        """Format date string for display"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y")
        except:
            return date_str
    
    def get_security_icon(self) -> str:
        """Return security icon for banking widgets"""
        return "security"
    
    def get_banking_actions(self) -> List[Dict[str, Any]]:
        """Return common banking actions"""
        return [
            {
                "type": "refresh",
                "label": "Refresh",
                "icon": "refresh",
                "description": "Refresh banking data"
            },
            {
                "type": "export",
                "label": "Export",
                "icon": "download",
                "description": "Export data to PDF/CSV"
            },
            {
                "type": "help",
                "label": "Help",
                "icon": "help",
                "description": "Get help with banking features"
            }
        ]
