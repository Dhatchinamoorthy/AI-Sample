import json
import asyncio
import os
from typing import Dict, List, Optional, Any
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, FunctionDeclaration, Tool, ToolConfig, Content, Part
import httpx
from app.config import settings
from app.services.external_apis import ExternalAPIService
from app.services.banking_api import BankingAPIService
from app.services.widget_service import WidgetService


class LLMService:
    """Service for handling LLM interactions with VertexAI and function calling"""
    
    def __init__(self):
        self.external_api_service = ExternalAPIService()
        self.banking_api_service = BankingAPIService()
        self.widget_service = WidgetService()
        self._initialize_vertex_ai()
        self._setup_functions()
    
    def _initialize_vertex_ai(self):
        """Initialize VertexAI with proper authentication"""
        try:
            # Check if we have required configuration
            if not settings.google_cloud_project:
                print("Google Cloud Project not configured. Using fallback mode.")
                self.model = None
                self.vertex_ai_available = False
                return
            
            if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
                # Use service account key file
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_application_credentials
                )
                vertexai.init(
                    project=settings.google_cloud_project,
                    location=settings.vertex_ai_location,
                    credentials=credentials
                )
            else:
                # Use default credentials (for local development with gcloud auth)
                vertexai.init(
                    project=settings.google_cloud_project,
                    location=settings.vertex_ai_location
                )
            
            self.model = GenerativeModel("gemini-2.5-flash")
            self.vertex_ai_available = True
            print("VertexAI initialized successfully")
        except Exception as e:
            print(f"Error initializing VertexAI: {e}")
            print("Using fallback mode - no AI responses available")
            self.model = None
            self.vertex_ai_available = False
    
    def _setup_functions(self):
        """Define function declarations for the LLM"""
        self.functions = [
            FunctionDeclaration(
                name="get_weather",
                description="Get current weather information for a specific location",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location (e.g., 'New York', 'London')"
                        }
                    },
                    "required": ["location"]
                }
            ),
            FunctionDeclaration(
                name="get_stock_price",
                description="Get current stock price and information for a specific stock symbol",
                parameters={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            FunctionDeclaration(
                name="get_news",
                description="Get latest news articles for a specific topic or category",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for news (e.g., 'technology', 'AI', 'stock market')"
                        },
                        "category": {
                            "type": "string",
                            "description": "News category (optional)",
                            "enum": ["business", "technology", "science", "health", "sports", "entertainment", "general"]
                        }
                    },
                    "required": ["query"]
                }
            ),
            FunctionDeclaration(
                name="get_time",
                description="Get current time for a specific timezone or location",
                parameters={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., 'UTC', 'America/New_York', 'Europe/London')"
                        },
                        "location": {
                            "type": "string",
                            "description": "City name for timezone lookup (optional)"
                        }
                    },
                    "required": []
                }
            ),
            FunctionDeclaration(
                name="get_top_stocks",
                description="Get the top 10 most actively traded stocks with current prices and market data",
                parameters={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top stocks to return (default: 10, max: 20)",
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": []
                }
            ),
            # Banking functions
            FunctionDeclaration(
                name="get_banking_accounts",
                description="Get all bank accounts or filter by account type (checking, savings, credit, investment, business)",
                parameters={
                    "type": "object",
                    "properties": {
                        "account_type": {
                            "type": "string",
                            "description": "Filter accounts by type (checking, savings, credit, investment, business)",
                            "enum": ["checking", "savings", "credit", "investment", "business"]
                        }
                    },
                    "required": []
                }
            ),
            FunctionDeclaration(
                name="get_account_transactions",
                description="Get transactions for a specific bank account",
                parameters={
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "string",
                            "description": "The account ID to get transactions for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of transactions to return (default: 10, max: 50)",
                            "minimum": 1,
                            "maximum": 50
                        },
                        "transaction_type": {
                            "type": "string",
                            "description": "Filter transactions by type",
                            "enum": ["debit", "credit", "transfer", "payment", "deposit", "withdrawal"]
                        }
                    },
                    "required": ["account_id"]
                }
            ),
            FunctionDeclaration(
                name="get_banking_offers",
                description="Get available banking offers and promotions",
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter offers by category",
                            "enum": ["savings", "credit", "investment", "loans", "mortgage"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of offers to return (default: 10, max: 20)",
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": []
                }
            ),
            FunctionDeclaration(
                name="get_payment_links",
                description="Get payment links and methods based on payment type",
                parameters={
                    "type": "object",
                    "properties": {
                        "payment_type": {
                            "type": "string",
                            "description": "Type of payment to get links for",
                            "enum": ["self", "3rd_party", "bill_pay", "international"]
                        },
                        "amount": {
                            "type": "number",
                            "description": "Payment amount (optional)"
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Payment recipient (optional)"
                        }
                    },
                    "required": ["payment_type"]
                }
            ),
            FunctionDeclaration(
                name="get_banker_contacts",
                description="Get banker contact information and availability",
                parameters={
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "description": "Filter bankers by department",
                            "enum": ["personal_banking", "business_banking", "investment_services", "mortgage_services", "commercial_banking"]
                        },
                        "specialization": {
                            "type": "string",
                            "description": "Filter bankers by specialization",
                            "enum": ["wealth_management", "small_business", "retirement_planning", "first_time_buyers", "large_corporations"]
                        }
                    },
                    "required": []
                }
            )
        ]
        
        self.tools = [Tool(function_declarations=self.functions)]
    
    async def process_message(self, message: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process user message and generate response with widgets"""
        try:
            # Check if VertexAI is available
            if not self.vertex_ai_available or not self.model:
                return await self._fallback_response(message)
            
            # Prepare the conversation
            conversation_parts = []
            
            # Add context if provided
            if context:
                for msg in context[-5:]:  # Keep last 5 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    conversation_parts.append(
                        Content(
                            role=role,
                            parts=[Part.from_text(content)]
                        )
                    )
            
            # Add current message
            conversation_parts.append(
                Content(
                    role="user",
                    parts=[Part.from_text(message)]
                )
            )
            
            # Generate response with function calling
            response = self.model.generate_content(
                conversation_parts,
                tools=self.tools,
                tool_config=ToolConfig(
                    function_calling_config=ToolConfig.FunctionCallingConfig(
                        mode=ToolConfig.FunctionCallingConfig.Mode.AUTO
                    )
                )
            )
            
            print("LLM Service response: ", response)
            
            # Process the response
            result = {
                "content": "",
                "widgets": []
            }
            
            # Handle function calls if any
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Execute function call
                        widget_data = await self._execute_function_call(part.function_call)
                        if widget_data:
                            result["widgets"].append(widget_data)
                    elif hasattr(part, 'text') and part.text:
                        result["content"] += part.text
            
            # If no widgets were generated but the response suggests widget usage,
            # try to extract intent and create appropriate widgets
            if not result["widgets"] and self._should_create_widget(message):
                widget_data = await self._extract_and_create_widget(message)
                if widget_data:
                    result["widgets"].append(widget_data)
            
            return result
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "widgets": []
            }
    
    async def _execute_function_call(self, function_call) -> Optional[Dict]:
        """Execute a function call and return widget data"""
        try:
            function_name = function_call.name
            args = dict(function_call.args)
            
            if function_name == "get_weather":
                location = args.get("location")
                weather_data = await self.external_api_service.get_weather(location)
                return self.widget_service.create_weather_widget(location, weather_data)
            
            elif function_name == "get_stock_price":
                symbol = args.get("symbol")
                stock_data = await self.external_api_service.get_stock_price(symbol)
                return self.widget_service.create_stock_widget(symbol, stock_data)
            
            elif function_name == "get_news":
                query = args.get("query")
                category = args.get("category")
                news_data = await self.external_api_service.get_news(query, category)
                return self.widget_service.create_news_widget(query, news_data)
            
            elif function_name == "get_time":
                timezone = args.get("timezone", "UTC")
                location = args.get("location")
                time_data = await self.external_api_service.get_time(timezone, location)
                return self.widget_service.create_clock_widget(timezone, location, time_data)
            
            elif function_name == "get_top_stocks":
                limit = args.get("limit", 10)
                stocks_data = await self.external_api_service.get_top_stocks(limit)
                return self.widget_service.create_top_stocks_widget(stocks_data)
            
            # Banking function calls
            elif function_name == "get_banking_accounts":
                account_type = args.get("account_type")
                accounts_data = await self.banking_api_service.get_accounts_by_type(account_type)
                return self.widget_service.create_banking_accounts_widget(accounts_data)
            
            elif function_name == "get_account_transactions":
                account_id = args.get("account_id")
                limit = args.get("limit", 10)
                transaction_type = args.get("transaction_type")
                transactions_data = await self.banking_api_service.get_account_transactions(account_id, limit, transaction_type)
                return self.widget_service.create_banking_transactions_widget(account_id, transactions_data)
            
            elif function_name == "get_banking_offers":
                category = args.get("category")
                limit = args.get("limit", 10)
                offers_data = await self.banking_api_service.get_offers(category, limit)
                return self.widget_service.create_banking_offers_widget(offers_data)
            
            elif function_name == "get_payment_links":
                payment_type = args.get("payment_type")
                amount = args.get("amount")
                recipient = args.get("recipient")
                payment_data = await self.banking_api_service.get_payment_links(payment_type, amount, recipient)
                return self.widget_service.create_banking_payments_widget(payment_type, payment_data)
            
            elif function_name == "get_banker_contacts":
                department = args.get("department")
                specialization = args.get("specialization")
                banker_data = await self.banking_api_service.get_banker_contacts(department, specialization)
                return self.widget_service.create_banking_banker_widget(banker_data)
            
        except Exception as e:
            print(f"Error executing function call {function_name}: {e}")
            return None
    
    def _should_create_widget(self, message: str) -> bool:
        """Determine if a message should trigger widget creation"""
        message_lower = message.lower()
        widget_keywords = [
            "weather", "temperature", "forecast", "rain", "sunny",
            "stock", "price", "trading", "market", "shares",
            "news", "latest", "headlines", "breaking",
            "time", "clock", "timezone", "what time",
            "top stocks", "most traded", "active stocks", "leaderboard", "top 10",
            # Banking keywords
            "account", "accounts", "banking", "bank", "balance", "checking", "savings", "credit",
            "transaction", "transactions", "payment", "payments", "transfer", "deposit", "withdrawal",
            "offer", "offers", "promotion", "promotions", "bonus", "cashback",
            "banker", "bankers", "contact", "advisor", "specialist", "manager"
        ]
        return any(keyword in message_lower for keyword in widget_keywords)
    
    async def _extract_and_create_widget(self, message: str) -> Optional[Dict]:
        """Extract widget intent from message and create appropriate widget"""
        message_lower = message.lower()
        
        try:
            if any(keyword in message_lower for keyword in ["weather", "temperature", "forecast"]):
                # Extract location from message
                location = self._extract_location(message)
                if location:
                    weather_data = await self.external_api_service.get_weather(location)
                    return self.widget_service.create_weather_widget(location, weather_data)
            
            elif any(keyword in message_lower for keyword in ["stock", "price", "trading"]):
                # Extract stock symbol from message
                symbol = self._extract_stock_symbol(message)
                if symbol:
                    stock_data = await self.external_api_service.get_stock_price(symbol)
                    return self.widget_service.create_stock_widget(symbol, stock_data)
            
            elif any(keyword in message_lower for keyword in ["news", "latest", "headlines"]):
                # Extract news query from message
                query = self._extract_news_query(message)
                news_data = await self.external_api_service.get_news(query)
                return self.widget_service.create_news_widget(query, news_data)
            
            elif any(keyword in message_lower for keyword in ["time", "clock", "timezone"]):
                # Extract timezone or location from message
                timezone = self._extract_timezone(message)
                location = self._extract_location(message)
                time_data = await self.external_api_service.get_time(timezone, location)
                return self.widget_service.create_clock_widget(timezone, location, time_data)
            
            elif any(keyword in message_lower for keyword in ["top stocks", "most traded", "active stocks", "leaderboard", "top 10"]):
                # Extract limit from message if specified
                limit = self._extract_top_stocks_limit(message)
                stocks_data = await self.external_api_service.get_top_stocks(limit)
                return self.widget_service.create_top_stocks_widget(stocks_data)
            
            # Banking widget extraction
            elif any(keyword in message_lower for keyword in ["account", "accounts", "banking", "balance"]):
                # Extract account type if specified
                account_type = self._extract_account_type(message)
                accounts_data = await self.banking_api_service.get_accounts_by_type(account_type)
                return self.widget_service.create_banking_accounts_widget(accounts_data)
            
            elif any(keyword in message_lower for keyword in ["transaction", "transactions", "payment", "payments"]):
                # Extract account ID and transaction type if specified
                account_id = self._extract_account_id(message)
                transaction_type = self._extract_transaction_type(message)
                limit = self._extract_transaction_limit(message)
                if account_id:
                    transactions_data = await self.banking_api_service.get_account_transactions(account_id, limit, transaction_type)
                    return self.widget_service.create_banking_transactions_widget(account_id, transactions_data)
            
            elif any(keyword in message_lower for keyword in ["offer", "offers", "promotion", "bonus", "cashback"]):
                # Extract offer category if specified
                category = self._extract_offer_category(message)
                limit = self._extract_offer_limit(message)
                offers_data = await self.banking_api_service.get_offers(category, limit)
                return self.widget_service.create_banking_offers_widget(offers_data)
            
            elif any(keyword in message_lower for keyword in ["banker", "bankers", "contact", "advisor", "specialist"]):
                # Extract department and specialization if specified
                department = self._extract_banker_department(message)
                specialization = self._extract_banker_specialization(message)
                banker_data = await self.banking_api_service.get_banker_contacts(department, specialization)
                return self.widget_service.create_banking_banker_widget(banker_data)
        
        except Exception as e:
            print(f"Error extracting widget from message: {e}")
            return None
    
    def _extract_location(self, message: str) -> Optional[str]:
        """Extract location from message"""
        # Simple location extraction - can be enhanced with NLP
        words = message.split()
        location_indicators = ["in", "at", "for", "of"]
        
        for i, word in enumerate(words):
            if word.lower() in location_indicators and i + 1 < len(words):
                return words[i + 1].title()
        
        # Try to find capitalized words that might be locations
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return "New York"  # Default location
    
    def _extract_stock_symbol(self, message: str) -> Optional[str]:
        """Extract stock symbol from message"""
        import re
        
        # Look for stock symbols (3-5 uppercase letters)
        symbols = re.findall(r'\b[A-Z]{3,5}\b', message.upper())
        if symbols:
            return symbols[0]
        
        # Look for common stock names and convert to symbols
        stock_mappings = {
            "apple": "AAPL", "google": "GOOGL", "microsoft": "MSFT",
            "amazon": "AMZN", "tesla": "TSLA", "meta": "META",
            "nvidia": "NVDA", "netflix": "NFLX"
        }
        
        message_lower = message.lower()
        for name, symbol in stock_mappings.items():
            if name in message_lower:
                return symbol
        
        return "AAPL"  # Default to Apple
    
    def _extract_news_query(self, message: str) -> str:
        """Extract news query from message"""
        # Remove common words and return the main topic
        stop_words = ["news", "latest", "about", "on", "the", "for", "get", "show", "me"]
        words = [word for word in message.split() if word.lower() not in stop_words]
        
        if words:
            return " ".join(words[:3])  # Take first 3 meaningful words
        
        return "technology"  # Default query
    
    def _extract_top_stocks_limit(self, message: str) -> int:
        """Extract limit for top stocks from message"""
        import re
        
        # Look for numbers in the message
        numbers = re.findall(r'\b(\d+)\b', message)
        
        if numbers:
            limit = int(numbers[0])
            # Ensure limit is within reasonable bounds
            return min(max(limit, 1), 20)
        
        return 10  # Default limit
    
    async def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Provide a fallback response when VertexAI is not available"""
        message_lower = message.lower()
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ['weather', 'temperature', 'forecast', 'rain', 'sunny']):
            return {
                "content": "I'd love to help you with weather information! However, I need to be configured with Google Cloud credentials to access weather data. Please set up your Google Cloud project and API keys to enable full functionality.",
                "widgets": []
            }
        elif any(word in message_lower for word in ['stock', 'price', 'market', 'trading', 'nasdaq']):
            return {
                "content": "I can help you get stock information! To enable this feature, please configure your Alpha Vantage API key in the backend configuration.",
                "widgets": []
            }
        elif any(word in message_lower for word in ['top stocks', 'most traded', 'active stocks', 'leaderboard', 'top 10']):
            # Top stocks widget can work with mock data
            try:
                limit = self._extract_top_stocks_limit(message)
                stocks_data = await self.external_api_service.get_top_stocks(limit)
                widget_data = self.widget_service.create_top_stocks_widget(stocks_data)
                return {
                    "content": f"Here are the top {limit} most actively traded stocks with current market data.",
                    "widgets": [widget_data]
                }
            except Exception as e:
                return {
                    "content": "I can show you the top traded stocks! However, there was an error retrieving the data.",
                    "widgets": []
                }
        elif any(word in message_lower for word in ['news', 'headlines', 'current events']):
            return {
                "content": "I'd be happy to fetch the latest news for you! Please configure your News API key to enable this feature.",
                "widgets": []
            }
        elif any(word in message_lower for word in ['time', 'clock', 'hour', 'minute']):
            # Clock widget doesn't need external APIs
            try:
                import datetime
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                return {
                    "content": f"The current time is {current_time}.",
                    "widgets": [{
                        "id": "clock-1",
                        "type": "clock",
                        "title": "Current Time",
                        "data": {"time": current_time},
                        "config": {"size": "small", "theme": "light"}
                    }]
                }
            except Exception:
                pass
        
        # Default response
        return {
            "content": f"Hello! I received your message: '{message}'. I'm an AI assistant that can help with weather, stocks, news, and more. To enable full functionality with widgets, please configure the required API keys (Google Cloud, Alpha Vantage, News API) in the backend configuration.",
            "widgets": []
        }
    
    def _extract_timezone(self, message: str) -> str:
        """Extract timezone from message"""
        timezone_mappings = {
            "new york": "America/New_York",
            "london": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "paris": "Europe/Paris",
            "sydney": "Australia/Sydney",
            "utc": "UTC"
        }
        
        message_lower = message.lower()
        for location, timezone in timezone_mappings.items():
            if location in message_lower:
                return timezone
        
        return "UTC"  # Default timezone
    
    def _extract_account_type(self, message: str) -> Optional[str]:
        """Extract account type from message"""
        message_lower = message.lower()
        account_types = {
            "checking": ["checking", "checking account"],
            "savings": ["savings", "savings account"],
            "credit": ["credit", "credit card", "credit account"],
            "investment": ["investment", "investment account", "portfolio"],
            "business": ["business", "business account"]
        }
        
        for account_type, keywords in account_types.items():
            if any(keyword in message_lower for keyword in keywords):
                return account_type
        
        return None
    
    def _extract_account_id(self, message: str) -> Optional[str]:
        """Extract account ID from message"""
        import re
        
        # Look for account ID patterns (ACC followed by numbers)
        account_patterns = [
            r'ACC\d+',
            r'account\s+(\w+)',
            r'account\s+id\s+(\w+)'
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        
        return "ACC001"  # Default account ID for demo
    
    def _extract_transaction_type(self, message: str) -> Optional[str]:
        """Extract transaction type from message"""
        message_lower = message.lower()
        transaction_types = {
            "debit": ["debit", "debit transaction"],
            "credit": ["credit", "credit transaction"],
            "transfer": ["transfer", "money transfer"],
            "payment": ["payment", "bill payment"],
            "deposit": ["deposit", "money deposit"],
            "withdrawal": ["withdrawal", "cash withdrawal"]
        }
        
        for tx_type, keywords in transaction_types.items():
            if any(keyword in message_lower for keyword in keywords):
                return tx_type
        
        return None
    
    def _extract_transaction_limit(self, message: str) -> int:
        """Extract transaction limit from message"""
        import re
        
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            limit = int(numbers[0])
            return min(max(limit, 1), 50)
        
        return 10  # Default limit
    
    def _extract_offer_category(self, message: str) -> Optional[str]:
        """Extract offer category from message"""
        message_lower = message.lower()
        categories = {
            "savings": ["savings", "savings offer"],
            "credit": ["credit", "credit card", "credit offer"],
            "investment": ["investment", "investment offer", "portfolio"],
            "loans": ["loan", "loans", "loan offer"],
            "mortgage": ["mortgage", "mortgage offer", "home loan"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_offer_limit(self, message: str) -> int:
        """Extract offer limit from message"""
        import re
        
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            limit = int(numbers[0])
            return min(max(limit, 1), 20)
        
        return 10  # Default limit
    
    def _extract_banker_department(self, message: str) -> Optional[str]:
        """Extract banker department from message"""
        message_lower = message.lower()
        departments = {
            "personal_banking": ["personal", "personal banking", "personal banker"],
            "business_banking": ["business", "business banking", "business banker"],
            "investment_services": ["investment", "investment services", "investment advisor"],
            "mortgage_services": ["mortgage", "mortgage services", "mortgage specialist"],
            "commercial_banking": ["commercial", "commercial banking", "commercial banker"]
        }
        
        for department, keywords in departments.items():
            if any(keyword in message_lower for keyword in keywords):
                return department
        
        return None
    
    def _extract_banker_specialization(self, message: str) -> Optional[str]:
        """Extract banker specialization from message"""
        message_lower = message.lower()
        specializations = {
            "wealth_management": ["wealth", "wealth management", "wealth advisor"],
            "small_business": ["small business", "small business banking"],
            "retirement_planning": ["retirement", "retirement planning", "retirement advisor"],
            "first_time_buyers": ["first time", "first time buyer", "first time home buyer"],
            "large_corporations": ["corporate", "large corporation", "enterprise"]
        }
        
        for specialization, keywords in specializations.items():
            if any(keyword in message_lower for keyword in keywords):
                return specialization
        
        return None
