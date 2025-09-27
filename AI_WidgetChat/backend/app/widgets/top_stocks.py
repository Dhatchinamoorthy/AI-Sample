from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class TopStocksWidget(BaseWidget):
    """Top 10 traded stocks widget implementation"""
    
    def get_widget_type(self) -> str:
        return "top_stocks"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "size": "large",
            "theme": "auto",
            "refreshInterval": 300,  # 5 minutes
            "showVolume": True,
            "showChange": True,
            "showMarketCap": True,
            "sortBy": "volume",  # volume, change, market_cap
            "market": "US"  # US, EU, ASIA
        }
    
    def create_widget_data(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create top stocks widget data"""
        try:
            # Format the stocks data
            formatted_data = self.format_data(stocks_data)
            
            # Create widget protocol
            widget_data = {
                "id": f"top_stocks_{int(datetime.now().timestamp())}",
                "type": "top_stocks",
                "title": "Top 10 Traded Stocks",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "alpha_vantage" if not any(stock.get("mock") for stock in stocks_data) else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create top stocks widget: {str(e)}")
    
    def format_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format top stocks data for display"""
        try:
            formatted_stocks = []
            
            for stock in raw_data[:10]:  # Limit to top 10
                # Calculate change percentage
                change_percent = stock.get("change_percent", "0%")
                if isinstance(change_percent, str):
                    change_percent = change_percent.replace("%", "")
                
                change_percent_float = float(change_percent) if change_percent else 0
                is_positive = change_percent_float >= 0
                
                formatted_stock = {
                    "symbol": stock.get("symbol", ""),
                    "company_name": stock.get("name", ""),
                    "price": {
                        "current": stock.get("price", 0),
                        "open": stock.get("open", 0),
                        "previous_close": stock.get("previous_close", 0)
                    },
                    "change": {
                        "amount": stock.get("change", 0),
                        "percentage": change_percent_float,
                        "is_positive": is_positive,
                        "formatted": f"{'+' if is_positive else ''}{stock.get('change', 0):.2f} ({'+' if is_positive else ''}{change_percent_float:.2f}%)"
                    },
                    "volume": stock.get("volume", 0),
                    "market_cap": stock.get("market_cap", 0),
                    "rank": len(formatted_stocks) + 1,
                    "timestamp": stock.get("timestamp", datetime.now().isoformat()),
                    "mock": stock.get("mock", False)
                }
                
                formatted_stocks.append(formatted_stock)
            
            return {
                "stocks": formatted_stocks,
                "total_count": len(formatted_stocks),
                "last_updated": datetime.now().isoformat(),
                "market": "US",
                "sort_by": "volume"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate top stocks widget configuration"""
        required_fields = ["size", "theme"]
        optional_fields = ["refreshInterval", "showVolume", "showChange", "showMarketCap", "sortBy", "market"]
        
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
        
        # Validate sort by
        if "sortBy" in config:
            if config["sortBy"] not in ["volume", "change", "market_cap"]:
                return False
        
        # Validate market
        if "market" in config:
            if config["market"] not in ["US", "EU", "ASIA"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["symbol", "price", "volume"]
    
    def get_optional_fields(self) -> List[str]:
        return ["change", "market_cap", "company_name", "rank"]
    
    def get_display_template(self) -> str:
        return "top_stocks"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            self.create_action("refresh"),
            self.create_action("configure"),
            {
                "type": "sort",
                "label": "Sort by Volume",
                "icon": "sort",
                "description": "Sort stocks by trading volume"
            },
            {
                "type": "sort",
                "label": "Sort by Change",
                "icon": "trending_up",
                "description": "Sort stocks by price change"
            },
            {
                "type": "export",
                "label": "Export Data",
                "icon": "download",
                "description": "Export top stocks data"
            }
        ]
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"top_stocks_error_{int(datetime.now().timestamp())}",
            "type": "top_stocks",
            "title": "Top Stocks Widget Error",
            "data": {
                "error": error_message,
                "stocks": [],
                "total_count": 0,
                "last_updated": datetime.now().isoformat(),
                "market": "US",
                "sort_by": "volume"
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
