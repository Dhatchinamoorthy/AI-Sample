from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.banking.base import BaseBankingWidget


class TransactionsWidget(BaseBankingWidget):
    """Banking transactions widget implementation"""
    
    def get_widget_type(self) -> str:
        return "banking_transactions"
    
    def get_default_config(self) -> Dict[str, Any]:
        base_config = super().get_banking_config()
        base_config.update({
            "size": "large",
            "theme": "banking",
            "show_transaction_details": True,
            "show_merchant_info": True,
            "show_categories": True,
            "group_by_date": True,
            "sort_by": "date",  # date, amount, type
            "limit": 10
        })
        return base_config
    
    def create_widget_data(self, account_id: str, transactions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create transactions widget data"""
        try:
            formatted_data = self.format_data(transactions_data)
            
            widget_data = {
                "id": f"transactions_{account_id}_{int(datetime.now().timestamp())}",
                "type": "banking_transactions",
                "title": f"Account Transactions",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "banking_api" if not transactions_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create transactions widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format transactions data for display"""
        try:
            transactions = raw_data.get("transactions", [])
            account_id = raw_data.get("account_id", "")
            account_balance = raw_data.get("account_balance", 0)
            
            # Calculate summary statistics
            total_debits = sum(tx.get("amount", 0) for tx in transactions if tx.get("amount", 0) < 0)
            total_credits = sum(tx.get("amount", 0) for tx in transactions if tx.get("amount", 0) > 0)
            
            # Group transactions by date
            transactions_by_date = {}
            for transaction in transactions:
                date_str = transaction.get("date", "")
                date_key = date_str.split("T")[0] if "T" in date_str else date_str
                if date_key not in transactions_by_date:
                    transactions_by_date[date_key] = []
                transactions_by_date[date_key].append(transaction)
            
            # Format each transaction
            formatted_transactions = []
            for transaction in transactions:
                amount = transaction.get("amount", 0)
                is_debit = amount < 0
                
                formatted_transaction = {
                    "id": transaction.get("id", ""),
                    "type": transaction.get("type", ""),
                    "amount": amount,
                    "amount_formatted": self.format_currency(abs(amount)),
                    "is_debit": is_debit,
                    "description": transaction.get("description", ""),
                    "merchant": transaction.get("merchant", ""),
                    "date": transaction.get("date", ""),
                    "date_formatted": self.format_date(transaction.get("date", "")),
                    "status": transaction.get("status", ""),
                    "category": transaction.get("category", ""),
                    "reference": transaction.get("reference", "")
                }
                formatted_transactions.append(formatted_transaction)
            
            return {
                "account_id": account_id,
                "transactions": formatted_transactions,
                "transactions_by_date": transactions_by_date,
                "summary": {
                    "total_transactions": len(transactions),
                    "account_balance": account_balance,
                    "account_balance_formatted": self.format_currency(account_balance),
                    "total_debits": abs(total_debits),
                    "total_debits_formatted": self.format_currency(abs(total_debits)),
                    "total_credits": total_credits,
                    "total_credits_formatted": self.format_currency(total_credits)
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate transactions widget configuration"""
        required_fields = ["size", "theme", "limit"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate limit
        if not isinstance(config["limit"], int) or config["limit"] < 1 or config["limit"] > 100:
            return False
        
        # Validate sort options
        if "sort_by" in config:
            if config["sort_by"] not in ["date", "amount", "type"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["transactions", "account_id"]
    
    def get_optional_fields(self) -> List[str]:
        return ["account_balance", "summary", "transactions_by_date"]
    
    def get_display_template(self) -> str:
        return "banking_transactions"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        actions = super().get_banking_actions()
        actions.extend([
            {
                "type": "filter",
                "label": "Filter Transactions",
                "icon": "filter_list",
                "description": "Filter by type, date, or amount"
            },
            {
                "type": "search",
                "label": "Search",
                "icon": "search",
                "description": "Search transactions"
            },
            {
                "type": "download",
                "label": "Download Statement",
                "icon": "download",
                "description": "Download transaction statement"
            },
            {
                "type": "categorize",
                "label": "Categorize",
                "icon": "category",
                "description": "Categorize transactions"
            }
        ])
        return actions
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"transactions_error_{int(datetime.now().timestamp())}",
            "type": "banking_transactions",
            "title": "Transactions Widget Error",
            "data": {
                "error": error_message,
                "transactions": [],
                "summary": {
                    "total_transactions": 0,
                    "account_balance": 0,
                    "account_balance_formatted": "$0.00",
                    "total_debits": 0,
                    "total_debits_formatted": "$0.00",
                    "total_credits": 0,
                    "total_credits_formatted": "$0.00"
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
