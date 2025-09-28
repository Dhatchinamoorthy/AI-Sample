from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.banking.base import BaseBankingWidget


class AccountsWidget(BaseBankingWidget):
    """Banking accounts widget implementation"""
    
    def get_widget_type(self) -> str:
        return "banking_accounts"
    
    def get_default_config(self) -> Dict[str, Any]:
        base_config = super().get_banking_config()
        base_config.update({
            "size": "large",
            "theme": "banking",
            "show_account_types": True,
            "show_balances": True,
            "show_last_activity": True,
            "group_by_type": True,
            "sort_by": "balance"  # balance, name, last_activity
        })
        return base_config
    
    def create_widget_data(self, accounts_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create accounts widget data"""
        try:
            formatted_data = self.format_data(accounts_data)
            
            widget_data = {
                "id": f"accounts_{int(datetime.now().timestamp())}",
                "type": "banking_accounts",
                "title": "My Accounts",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "banking_api" if not accounts_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create accounts widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format accounts data for display"""
        try:
            accounts = raw_data.get("accounts", [])
            
            # Calculate totals
            total_balance = sum(acc.get("balance", 0) for acc in accounts)
            active_accounts = len([acc for acc in accounts if acc.get("status") == "active"])
            
            # Group accounts by type
            accounts_by_type = {}
            for account in accounts:
                acc_type = account.get("type", "other")
                if acc_type not in accounts_by_type:
                    accounts_by_type[acc_type] = []
                accounts_by_type[acc_type].append(account)
            
            # Format each account
            formatted_accounts = []
            for account in accounts:
                formatted_account = {
                    "id": account.get("id", ""),
                    "account_number": account.get("account_number", ""),
                    "name": account.get("name", ""),
                    "type": account.get("type", ""),
                    "balance": account.get("balance", 0),
                    "balance_formatted": self.format_currency(account.get("balance", 0)),
                    "currency": account.get("currency", "USD"),
                    "status": account.get("status", "unknown"),
                    "last_activity": account.get("last_activity", ""),
                    "last_activity_formatted": self.format_date(account.get("last_activity", "")),
                    "is_positive": account.get("balance", 0) >= 0
                }
                formatted_accounts.append(formatted_account)
            
            return {
                "accounts": formatted_accounts,
                "accounts_by_type": accounts_by_type,
                "summary": {
                    "total_accounts": len(accounts),
                    "active_accounts": active_accounts,
                    "total_balance": total_balance,
                    "total_balance_formatted": self.format_currency(total_balance),
                    "account_types": list(accounts_by_type.keys())
                },
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate accounts widget configuration"""
        required_fields = ["size", "theme", "show_balances"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate size
        if config["size"] not in ["small", "medium", "large"]:
            return False
        
        # Validate sort options
        if "sort_by" in config:
            if config["sort_by"] not in ["balance", "name", "last_activity"]:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["accounts", "total_count"]
    
    def get_optional_fields(self) -> List[str]:
        return ["account_types", "summary"]
    
    def get_display_template(self) -> str:
        return "banking_accounts"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        actions = super().get_banking_actions()
        actions.extend([
            {
                "type": "filter",
                "label": "Filter by Type",
                "icon": "filter_list",
                "description": "Filter accounts by type"
            },
            {
                "type": "sort",
                "label": "Sort Accounts",
                "icon": "sort",
                "description": "Change sorting order"
            },
            {
                "type": "add_account",
                "label": "Add Account",
                "icon": "add",
                "description": "Add new account"
            }
        ])
        return actions
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"accounts_error_{int(datetime.now().timestamp())}",
            "type": "banking_accounts",
            "title": "Accounts Widget Error",
            "data": {
                "error": error_message,
                "accounts": [],
                "summary": {
                    "total_accounts": 0,
                    "active_accounts": 0,
                    "total_balance": 0,
                    "total_balance_formatted": "$0.00",
                    "account_types": []
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
