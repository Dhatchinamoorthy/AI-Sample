from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.banking.base import BaseBankingWidget


class PaymentsWidget(BaseBankingWidget):
    """Banking payments widget implementation"""
    
    def get_widget_type(self) -> str:
        return "banking_payments"
    
    def get_default_config(self) -> Dict[str, Any]:
        base_config = super().get_banking_config()
        base_config.update({
            "size": "medium",
            "theme": "banking",
            "show_payment_details": True,
            "show_fees": True,
            "show_processing_time": True,
            "group_by_type": True,
            "sort_by": "fee",  # fee, processing_time, type
            "default_amount": None
        })
        return base_config
    
    def create_widget_data(self, payment_type: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payments widget data"""
        try:
            formatted_data = self.format_data(payment_data)
            
            widget_data = {
                "id": f"payments_{payment_type}_{int(datetime.now().timestamp())}",
                "type": "banking_payments",
                "title": f"Payment Options - {payment_type.replace('_', ' ').title()}",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "banking_api" if not payment_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create payments widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format payments data for display"""
        try:
            payment_links = raw_data.get("payment_links", [])
            payment_type = raw_data.get("payment_type", "")
            amount = raw_data.get("amount")
            recipient = raw_data.get("recipient")
            
            # Group payment methods by type
            payment_methods_by_type = {}
            for method in payment_links:
                method_type = method.get("type", "other")
                if method_type not in payment_methods_by_type:
                    payment_methods_by_type[method_type] = []
                payment_methods_by_type[method_type].append(method)
            
            # Format each payment method
            formatted_methods = []
            for method in payment_links:
                fee = method.get("fee", 0)
                processing_time = method.get("processing_time", "")
                
                formatted_method = {
                    "id": method.get("id", ""),
                    "type": method.get("type", ""),
                    "name": method.get("name", ""),
                    "description": method.get("description", ""),
                    "url": method.get("url", ""),
                    "fee": fee,
                    "fee_formatted": self.format_currency(fee),
                    "processing_time": processing_time,
                    "is_free": fee == 0,
                    "is_instant": "instant" in processing_time.lower(),
                    "recommended": self._is_recommended_method(method, amount)
                }
                formatted_methods.append(formatted_method)
            
            # Sort by recommendation and fee
            formatted_methods.sort(key=lambda x: (not x["recommended"], x["fee"]))
            
            return {
                "payment_type": payment_type,
                "payment_methods": formatted_methods,
                "payment_methods_by_type": payment_methods_by_type,
                "context": {
                    "amount": amount,
                    "amount_formatted": self.format_currency(amount) if amount else None,
                    "recipient": recipient
                },
                "summary": {
                    "total_methods": len(payment_links),
                    "free_methods": len([m for m in formatted_methods if m["is_free"]]),
                    "instant_methods": len([m for m in formatted_methods if m["is_instant"]]),
                    "available_types": list(payment_methods_by_type.keys())
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _is_recommended_method(self, method: Dict[str, Any], amount: Optional[float]) -> bool:
        """Determine if payment method is recommended based on amount and type"""
        method_type = method.get("type", "")
        fee = method.get("fee", 0)
        
        # Free methods are always recommended
        if fee == 0:
            return True
        
        # For small amounts, prefer free methods
        if amount and amount < 100 and fee > 0:
            return False
        
        # For large amounts, prefer secure methods
        if amount and amount > 1000:
            return method_type in ["wire_transfer", "international_wire"]
        
        # Default recommendation logic
        return method_type in ["internal_transfer", "ach_transfer"]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate payments widget configuration"""
        required_fields = ["size", "theme"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate sort options
        if "sort_by" in config:
            if config["sort_by"] not in ["fee", "processing_time", "type"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["payment_links", "payment_type"]
    
    def get_optional_fields(self) -> List[str]:
        return ["amount", "recipient", "available_methods", "summary"]
    
    def get_display_template(self) -> str:
        return "banking_payments"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        actions = super().get_banking_actions()
        actions.extend([
            {
                "type": "initiate_payment",
                "label": "Initiate Payment",
                "icon": "payment",
                "description": "Start payment process"
            },
            {
                "type": "schedule",
                "label": "Schedule Payment",
                "icon": "schedule",
                "description": "Schedule future payment"
            },
            {
                "type": "recurring",
                "label": "Set Recurring",
                "icon": "repeat",
                "description": "Set up recurring payment"
            },
            {
                "type": "history",
                "label": "Payment History",
                "icon": "history",
                "description": "View payment history"
            }
        ])
        return actions
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"payments_error_{int(datetime.now().timestamp())}",
            "type": "banking_payments",
            "title": "Payments Widget Error",
            "data": {
                "error": error_message,
                "payment_methods": [],
                "summary": {
                    "total_methods": 0,
                    "free_methods": 0,
                    "instant_methods": 0,
                    "available_types": []
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
