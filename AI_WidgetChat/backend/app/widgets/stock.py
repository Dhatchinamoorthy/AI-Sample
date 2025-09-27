from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class StockWidget(BaseWidget):
    """Stock widget implementation"""
    
    def get_widget_type(self) -> str:
        return "stock"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "size": "medium",
            "theme": "auto",
            "refreshInterval": 60,  # 1 minute
            "showChart": True,
            "showVolume": True,
            "showChange": True,
            "showHighLow": True,
            "chartType": "line",  # line or bar
            "timeRange": "1D"  # 1D, 1W, 1M, 3M, 1Y
        }
    
    def create_widget_data(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create stock widget data"""
        try:
            # Format the stock data
            formatted_data = self.format_data(stock_data)
            
            # Create widget protocol
            widget_data = {
                "id": f"stock_{symbol.lower()}_{int(datetime.now().timestamp())}",
                "type": "stock",
                "title": f"{symbol.upper()} Stock Price",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "alpha_vantage" if not stock_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create stock widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format stock data for display"""
        try:
            # Calculate change percentage
            change_percent = raw_data.get("change_percent", "0%")
            if isinstance(change_percent, str):
                change_percent = change_percent.replace("%", "")
            
            change_percent_float = float(change_percent) if change_percent else 0
            is_positive = change_percent_float >= 0
            
            return {
                "symbol": raw_data.get("symbol", ""),
                "company_name": raw_data.get("name", ""),
                "price": {
                    "current": raw_data.get("price", 0),
                    "open": raw_data.get("open", 0),
                    "previous_close": raw_data.get("previous_close", 0)
                },
                "change": {
                    "amount": raw_data.get("change", 0),
                    "percentage": change_percent_float,
                    "is_positive": is_positive,
                    "formatted": f"{'+' if is_positive else ''}{raw_data.get('change', 0):.2f} ({'+' if is_positive else ''}{change_percent_float:.2f}%)"
                },
                "range": {
                    "high": raw_data.get("high", 0),
                    "low": raw_data.get("low", 0)
                },
                "volume": raw_data.get("volume", 0),
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate stock widget configuration"""
        required_fields = ["size", "theme"]
        optional_fields = ["refreshInterval", "showChart", "showVolume", "showChange", "showHighLow", "chartType", "timeRange"]
        
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
        
        # Validate chart type
        if "chartType" in config:
            if config["chartType"] not in ["line", "bar"]:
                return False
        
        # Validate time range
        if "timeRange" in config:
            if config["timeRange"] not in ["1D", "1W", "1M", "3M", "1Y"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["symbol", "price", "change"]
    
    def get_optional_fields(self) -> List[str]:
        return ["volume", "high", "low", "open", "previous_close", "company_name"]
    
    def get_display_template(self) -> str:
        return "stock"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            self.create_action("refresh"),
            self.create_action("configure"),
            {
                "type": "chart",
                "label": "View Chart",
                "icon": "trending_up",
                "description": "View detailed price chart"
            },
            {
                "type": "news",
                "label": "Related News",
                "icon": "newspaper",
                "description": "View news about this stock"
            }
        ]
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"stock_error_{int(datetime.now().timestamp())}",
            "type": "stock",
            "title": "Stock Widget Error",
            "data": {
                "error": error_message,
                "symbol": "ERROR",
                "company_name": "Error Loading Stock Data",
                "price": {
                    "current": 0,
                    "open": 0,
                    "previous_close": 0
                },
                "change": {
                    "amount": 0,
                    "percentage": 0,
                    "is_positive": True,
                    "formatted": "0.00 (0.00%)"
                },
                "range": {
                    "high": 0,
                    "low": 0
                },
                "volume": 0,
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
