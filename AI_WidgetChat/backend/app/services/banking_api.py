import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from app.config import settings


class BankingAPIService:
    """Service for handling banking-related API calls and data management"""
    
    def __init__(self):
        self.timeout = 10.0
        self.base_url = "https://api.banking.example.com"  # Replace with actual banking API
        self.mock_data_enabled = True  # Enable mock data for development
    
    async def get_accounts_by_type(self, account_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all accounts or filter by account type"""
        if self.mock_data_enabled:
            return self._get_mock_accounts_data(account_type)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/accounts"
                params = {}
                if account_type:
                    params["type"] = account_type
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "accounts": data.get("accounts", []),
                    "total_count": data.get("total_count", 0),
                    "account_types": data.get("account_types", []),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching accounts: {e}")
            return self._get_mock_accounts_data(account_type)
    
    async def get_account_transactions(self, account_id: str, limit: int = 10, 
                                     transaction_type: Optional[str] = None) -> Dict[str, Any]:
        """Get transactions for a specific account"""
        if self.mock_data_enabled:
            return self._get_mock_transactions_data(account_id, limit, transaction_type)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/accounts/{account_id}/transactions"
                params = {"limit": limit}
                if transaction_type:
                    params["type"] = transaction_type
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "account_id": account_id,
                    "transactions": data.get("transactions", []),
                    "total_count": data.get("total_count", 0),
                    "account_balance": data.get("account_balance", 0),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return self._get_mock_transactions_data(account_id, limit, transaction_type)
    
    async def get_offers(self, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get available banking offers and promotions"""
        if self.mock_data_enabled:
            return self._get_mock_offers_data(category, limit)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/offers"
                params = {"limit": limit}
                if category:
                    params["category"] = category
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "offers": data.get("offers", []),
                    "total_count": data.get("total_count", 0),
                    "categories": data.get("categories", []),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching offers: {e}")
            return self._get_mock_offers_data(category, limit)
    
    async def get_payment_links(self, payment_type: str, amount: Optional[float] = None, 
                               recipient: Optional[str] = None) -> Dict[str, Any]:
        """Get payment links based on payment type and parameters"""
        if self.mock_data_enabled:
            return self._get_mock_payment_links_data(payment_type, amount, recipient)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/payments/links"
                params = {"type": payment_type}
                if amount:
                    params["amount"] = amount
                if recipient:
                    params["recipient"] = recipient
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "payment_links": data.get("links", []),
                    "payment_type": payment_type,
                    "available_methods": data.get("available_methods", []),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching payment links: {e}")
            return self._get_mock_payment_links_data(payment_type, amount, recipient)
    
    async def get_banker_contacts(self, department: Optional[str] = None, 
                                 specialization: Optional[str] = None) -> Dict[str, Any]:
        """Get banker contact information"""
        if self.mock_data_enabled:
            return self._get_mock_banker_contacts_data(department, specialization)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/bankers"
                params = {}
                if department:
                    params["department"] = department
                if specialization:
                    params["specialization"] = specialization
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "bankers": data.get("bankers", []),
                    "total_count": data.get("total_count", 0),
                    "departments": data.get("departments", []),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching banker contacts: {e}")
            return self._get_mock_banker_contacts_data(department, specialization)
    
    def _get_mock_accounts_data(self, account_type: Optional[str] = None) -> Dict[str, Any]:
        """Return mock accounts data for testing"""
        import random
        
        all_accounts = [
            {
                "id": "ACC001",
                "account_number": "****1234",
                "type": "checking",
                "name": "Primary Checking",
                "balance": 2547.89,
                "currency": "USD",
                "status": "active",
                "last_activity": "2024-01-15T10:30:00Z"
            },
            {
                "id": "ACC002", 
                "account_number": "****5678",
                "type": "savings",
                "name": "High Yield Savings",
                "balance": 15420.50,
                "currency": "USD",
                "status": "active",
                "last_activity": "2024-01-14T15:45:00Z"
            },
            {
                "id": "ACC003",
                "account_number": "****9012",
                "type": "credit",
                "name": "Premium Credit Card",
                "balance": -1250.75,
                "currency": "USD",
                "status": "active",
                "last_activity": "2024-01-15T09:15:00Z"
            },
            {
                "id": "ACC004",
                "account_number": "****3456",
                "type": "investment",
                "name": "Investment Portfolio",
                "balance": 45678.25,
                "currency": "USD",
                "status": "active",
                "last_activity": "2024-01-15T11:20:00Z"
            },
            {
                "id": "ACC005",
                "account_number": "****7890",
                "type": "business",
                "name": "Business Checking",
                "balance": 8750.00,
                "currency": "USD",
                "status": "active",
                "last_activity": "2024-01-15T08:30:00Z"
            }
        ]
        
        # Filter by account type if specified
        if account_type:
            filtered_accounts = [acc for acc in all_accounts if acc["type"] == account_type]
        else:
            filtered_accounts = all_accounts
        
        return {
            "accounts": filtered_accounts,
            "total_count": len(filtered_accounts),
            "account_types": ["checking", "savings", "credit", "investment", "business"],
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_transactions_data(self, account_id: str, limit: int, 
                                   transaction_type: Optional[str] = None) -> Dict[str, Any]:
        """Return mock transactions data for testing"""
        import random
        
        transaction_types = ["debit", "credit", "transfer", "payment", "deposit", "withdrawal"]
        merchants = ["Amazon", "Starbucks", "Shell", "Walmart", "Netflix", "Spotify", "Apple", "Google"]
        
        transactions = []
        for i in range(min(limit, 15)):
            tx_type = random.choice(transaction_types)
            amount = round(random.uniform(5, 500), 2)
            is_debit = tx_type in ["debit", "payment", "withdrawal"]
            
            transaction = {
                "id": f"TXN{1000 + i}",
                "account_id": account_id,
                "type": tx_type,
                "amount": amount if not is_debit else -amount,
                "description": f"{random.choice(merchants)} - {tx_type.title()}",
                "merchant": random.choice(merchants),
                "date": datetime.now().replace(day=random.randint(1, 15)).isoformat(),
                "status": random.choice(["completed", "pending", "processing"]),
                "category": random.choice(["food", "transportation", "entertainment", "shopping", "utilities"]),
                "reference": f"REF{random.randint(100000, 999999)}"
            }
            
            if not transaction_type or transaction["type"] == transaction_type:
                transactions.append(transaction)
        
        # Sort by date (most recent first)
        transactions.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "account_id": account_id,
            "transactions": transactions[:limit],
            "total_count": len(transactions),
            "account_balance": round(random.uniform(1000, 50000), 2),
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_offers_data(self, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Return mock offers data for testing"""
        import random
        
        all_offers = [
            {
                "id": "OFFER001",
                "title": "High Yield Savings Bonus",
                "description": "Earn 5.25% APY on new savings deposits up to $10,000",
                "category": "savings",
                "type": "bonus",
                "value": "$525",
                "valid_until": "2024-03-31T23:59:59Z",
                "requirements": "Minimum $1,000 deposit",
                "status": "active"
            },
            {
                "id": "OFFER002",
                "title": "Credit Card Cashback",
                "description": "Get 3% cashback on all dining and entertainment purchases",
                "category": "credit",
                "type": "cashback",
                "value": "3%",
                "valid_until": "2024-12-31T23:59:59Z",
                "requirements": "Minimum $500 monthly spend",
                "status": "active"
            },
            {
                "id": "OFFER003",
                "title": "Investment Account Bonus",
                "description": "Receive $100 bonus when you open a new investment account",
                "category": "investment",
                "type": "bonus",
                "value": "$100",
                "valid_until": "2024-06-30T23:59:59Z",
                "requirements": "Minimum $5,000 initial investment",
                "status": "active"
            },
            {
                "id": "OFFER004",
                "title": "Business Loan Special Rate",
                "description": "Special 4.5% APR on business loans up to $100,000",
                "category": "loans",
                "type": "rate_reduction",
                "value": "4.5% APR",
                "valid_until": "2024-04-30T23:59:59Z",
                "requirements": "Existing business account holders",
                "status": "active"
            },
            {
                "id": "OFFER005",
                "title": "Mortgage Rate Lock",
                "description": "Lock in today's rates for 60 days on your mortgage application",
                "category": "mortgage",
                "type": "rate_lock",
                "value": "60 days",
                "valid_until": "2024-05-15T23:59:59Z",
                "requirements": "Pre-approved mortgage application",
                "status": "active"
            }
        ]
        
        # Filter by category if specified
        if category:
            filtered_offers = [offer for offer in all_offers if offer["category"] == category]
        else:
            filtered_offers = all_offers
        
        return {
            "offers": filtered_offers[:limit],
            "total_count": len(filtered_offers),
            "categories": ["savings", "credit", "investment", "loans", "mortgage"],
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_payment_links_data(self, payment_type: str, amount: Optional[float], 
                                    recipient: Optional[str]) -> Dict[str, Any]:
        """Return mock payment links data for testing"""
        import random
        
        payment_methods = {
            "self": [
                {
                    "id": "PAY001",
                    "type": "internal_transfer",
                    "name": "Transfer to Own Account",
                    "description": "Transfer money between your own accounts",
                    "url": "https://bank.example.com/transfer",
                    "fee": 0.00,
                    "processing_time": "Instant"
                }
            ],
            "3rd_party": [
                {
                    "id": "PAY002",
                    "type": "wire_transfer",
                    "name": "Wire Transfer",
                    "description": "Send money to external bank accounts",
                    "url": "https://bank.example.com/wire",
                    "fee": 25.00,
                    "processing_time": "1-2 business days"
                },
                {
                    "id": "PAY003",
                    "type": "ach_transfer",
                    "name": "ACH Transfer",
                    "description": "Electronic transfer to US bank accounts",
                    "url": "https://bank.example.com/ach",
                    "fee": 3.00,
                    "processing_time": "1-3 business days"
                }
            ],
            "bill_pay": [
                {
                    "id": "PAY004",
                    "type": "bill_payment",
                    "name": "Bill Payment",
                    "description": "Pay bills and utilities",
                    "url": "https://bank.example.com/bills",
                    "fee": 0.00,
                    "processing_time": "1-2 business days"
                }
            ],
            "international": [
                {
                    "id": "PAY005",
                    "type": "international_wire",
                    "name": "International Wire",
                    "description": "Send money internationally",
                    "url": "https://bank.example.com/international",
                    "fee": 45.00,
                    "processing_time": "2-5 business days"
                }
            ]
        }
        
        available_methods = payment_methods.get(payment_type, [])
        
        return {
            "payment_links": available_methods,
            "payment_type": payment_type,
            "available_methods": list(payment_methods.keys()),
            "amount": amount,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_banker_contacts_data(self, department: Optional[str], 
                                       specialization: Optional[str]) -> Dict[str, Any]:
        """Return mock banker contacts data for testing"""
        import random
        
        all_bankers = [
            {
                "id": "BANKER001",
                "name": "Sarah Johnson",
                "title": "Senior Personal Banker",
                "department": "personal_banking",
                "specialization": "wealth_management",
                "email": "sarah.johnson@bank.com",
                "phone": "+1-555-0101",
                "availability": "Mon-Fri 9AM-5PM",
                "experience": "8 years",
                "languages": ["English", "Spanish"]
            },
            {
                "id": "BANKER002",
                "name": "Michael Chen",
                "title": "Business Banking Specialist",
                "department": "business_banking",
                "specialization": "small_business",
                "email": "michael.chen@bank.com",
                "phone": "+1-555-0102",
                "availability": "Mon-Fri 8AM-6PM",
                "experience": "12 years",
                "languages": ["English", "Mandarin"]
            },
            {
                "id": "BANKER003",
                "name": "Emily Rodriguez",
                "title": "Investment Advisor",
                "department": "investment_services",
                "specialization": "retirement_planning",
                "email": "emily.rodriguez@bank.com",
                "phone": "+1-555-0103",
                "availability": "Mon-Fri 9AM-4PM",
                "experience": "6 years",
                "languages": ["English", "Spanish"]
            },
            {
                "id": "BANKER004",
                "name": "David Kim",
                "title": "Mortgage Specialist",
                "department": "mortgage_services",
                "specialization": "first_time_buyers",
                "email": "david.kim@bank.com",
                "phone": "+1-555-0104",
                "availability": "Mon-Sat 9AM-7PM",
                "experience": "10 years",
                "languages": ["English", "Korean"]
            },
            {
                "id": "BANKER005",
                "name": "Lisa Thompson",
                "title": "Commercial Banking Manager",
                "department": "commercial_banking",
                "specialization": "large_corporations",
                "email": "lisa.thompson@bank.com",
                "phone": "+1-555-0105",
                "availability": "Mon-Fri 8AM-5PM",
                "experience": "15 years",
                "languages": ["English"]
            }
        ]
        
        # Filter by department and specialization
        filtered_bankers = all_bankers
        if department:
            filtered_bankers = [b for b in filtered_bankers if b["department"] == department]
        if specialization:
            filtered_bankers = [b for b in filtered_bankers if b["specialization"] == specialization]
        
        return {
            "bankers": filtered_bankers,
            "total_count": len(filtered_bankers),
            "departments": ["personal_banking", "business_banking", "investment_services", 
                          "mortgage_services", "commercial_banking"],
            "specializations": ["wealth_management", "small_business", "retirement_planning", 
                              "first_time_buyers", "large_corporations"],
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
