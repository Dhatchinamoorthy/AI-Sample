import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.widgets.base import BaseWidget
from app.widgets.weather import WeatherWidget
from app.widgets.stock import StockWidget
from app.widgets.news import NewsWidget
from app.widgets.clock import ClockWidget
from app.widgets.top_stocks import TopStocksWidget
# Banking widgets
from app.widgets.banking.accounts import AccountsWidget
from app.widgets.banking.transactions import TransactionsWidget
from app.widgets.banking.offers import OffersWidget
from app.widgets.banking.payments import PaymentsWidget
from app.widgets.banking.banker import BankerWidget


class WidgetService:
    """Service for managing widget protocols and data"""
    
    def __init__(self):
        self.widget_registry = {
            "weather": WeatherWidget,
            "stock": StockWidget,
            "news": NewsWidget,
            "clock": ClockWidget,
            "top_stocks": TopStocksWidget,
            # Banking widgets
            "banking_accounts": AccountsWidget,
            "banking_transactions": TransactionsWidget,
            "banking_offers": OffersWidget,
            "banking_payments": PaymentsWidget,
            "banking_banker": BankerWidget
        }
    
    def create_weather_widget(self, location: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a weather widget with the provided data"""
        widget = WeatherWidget()
        return widget.create_widget_data(location, weather_data)
    
    def create_stock_widget(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a stock widget with the provided data"""
        widget = StockWidget()
        return widget.create_widget_data(symbol, stock_data)
    
    def create_news_widget(self, query: str, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a news widget with the provided data"""
        widget = NewsWidget()
        return widget.create_widget_data(query, news_data)
    
    def create_clock_widget(self, timezone: str, location: Optional[str], time_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clock widget with the provided data"""
        widget = ClockWidget()
        return widget.create_widget_data(timezone, location, time_data)
    
    def create_top_stocks_widget(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a top stocks widget with the provided data"""
        widget = TopStocksWidget()
        return widget.create_widget_data(stocks_data)
    
    # Banking widget creation methods
    def create_banking_accounts_widget(self, accounts_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a banking accounts widget with the provided data"""
        widget = AccountsWidget()
        return widget.create_widget_data(accounts_data)
    
    def create_banking_transactions_widget(self, account_id: str, transactions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a banking transactions widget with the provided data"""
        widget = TransactionsWidget()
        return widget.create_widget_data(account_id, transactions_data)
    
    def create_banking_offers_widget(self, offers_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a banking offers widget with the provided data"""
        widget = OffersWidget()
        return widget.create_widget_data(offers_data)
    
    def create_banking_payments_widget(self, payment_type: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a banking payments widget with the provided data"""
        widget = PaymentsWidget()
        return widget.create_widget_data(payment_type, payment_data)
    
    def create_banking_banker_widget(self, banker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a banking banker widget with the provided data"""
        widget = BankerWidget()
        return widget.create_widget_data(banker_data)
    
    def get_widget_by_type(self, widget_type: str) -> Optional[BaseWidget]:
        """Get widget class by type"""
        return self.widget_registry.get(widget_type)
    
    def get_available_widget_types(self) -> List[str]:
        """Get list of available widget types"""
        return list(self.widget_registry.keys())
    
    def validate_widget_config(self, widget_type: str, config: Dict[str, Any]) -> bool:
        """Validate widget configuration"""
        widget_class = self.get_widget_by_type(widget_type)
        if not widget_class:
            return False
        
        try:
            # Create a temporary widget instance to validate config
            widget = widget_class()
            return widget.validate_config(config)
        except Exception:
            return False
    
    def get_widget_default_config(self, widget_type: str) -> Dict[str, Any]:
        """Get default configuration for a widget type"""
        widget_class = self.get_widget_by_type(widget_type)
        if not widget_class:
            return {}
        
        widget = widget_class()
        return widget.get_default_config()
    
    def create_widget_protocol(
        self,
        widget_type: str,
        title: str,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a standardized widget protocol object"""
        widget_class = self.get_widget_by_type(widget_type)
        if not widget_class:
            raise ValueError(f"Unknown widget type: {widget_type}")
        
        widget = widget_class()
        default_config = widget.get_default_config()
        
        if config:
            default_config.update(config)
        
        return {
            "id": str(uuid.uuid4()),
            "type": widget_type,
            "title": title,
            "data": data,
            "config": default_config,
            "actions": actions or [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "ai_widget_chat",
                "version": "1.0.0"
            }
        }
    
    def update_widget_data(self, widget_id: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update widget data (for real-time updates)"""
        return {
            "id": widget_id,
            "data": new_data,
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
    
    def get_widget_refresh_interval(self, widget_type: str) -> int:
        """Get refresh interval for a widget type (in seconds)"""
        refresh_intervals = {
            "weather": 300,    # 5 minutes
            "stock": 60,       # 1 minute
            "news": 600,       # 10 minutes
            "clock": 30,       # 30 seconds
            # Banking widgets
            "banking_accounts": 300,      # 5 minutes
            "banking_transactions": 60,   # 1 minute
            "banking_offers": 3600,       # 1 hour
            "banking_payments": 300,      # 5 minutes
            "banking_banker": 1800        # 30 minutes
        }
        return refresh_intervals.get(widget_type, 300)
    
    def should_auto_refresh(self, widget_type: str) -> bool:
        """Determine if a widget should auto-refresh"""
        auto_refresh_widgets = ["weather", "stock", "clock", "banking_accounts", "banking_transactions"]
        return widget_type in auto_refresh_widgets
