import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import pytz
from app.config import settings


class ExternalAPIService:
    """Service for handling external API calls to third-party services"""
    
    def __init__(self):
        self.timeout = 10.0
        self.rate_limits = {
            "openweather": {"calls": 0, "reset_time": datetime.now()},
            "alpha_vantage": {"calls": 0, "reset_time": datetime.now()},
            "news_api": {"calls": 0, "reset_time": datetime.now()}
        }
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API"""
        if not settings.openweather_api_key:
            return self._get_mock_weather_data(location)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": location,
                    "appid": settings.openweather_api_key,
                    "units": "metric"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "location": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "wind_speed": data["wind"]["speed"],
                    "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_mock_weather_data(location)
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Alpha Vantage API"""
        if not settings.alpha_vantage_api_key:
            return self._get_mock_stock_data(symbol)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "Global Quote" not in data:
                    return self._get_mock_stock_data(symbol)
                
                quote = data["Global Quote"]
                
                return {
                    "symbol": quote["01. symbol"],
                    "name": self._get_company_name(symbol),
                    "price": float(quote["05. price"]),
                    "change": float(quote["09. change"]),
                    "change_percent": quote["10. change percent"].replace("%", ""),
                    "volume": int(quote["06. volume"]),
                    "high": float(quote["03. high"]),
                    "low": float(quote["04. low"]),
                    "open": float(quote["02. open"]),
                    "previous_close": float(quote["08. previous close"]),
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return self._get_mock_stock_data(symbol)
    
    async def get_news(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Get news data from NewsAPI"""
        if not settings.news_api_key:
            return self._get_mock_news_data(query)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": settings.news_api_key,
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "language": "en"
                }
                
                if category:
                    params["category"] = category
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = []
                for article in data.get("articles", []):
                    articles.append({
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "source": article["source"]["name"],
                        "published_at": article["publishedAt"],
                        "url_to_image": article.get("urlToImage")
                    })
                
                return {
                    "query": query,
                    "total_results": data["totalResults"],
                    "articles": articles,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching news data: {e}")
            return self._get_mock_news_data(query)
    
    async def get_time(self, timezone_str: str = "UTC", location: Optional[str] = None) -> Dict[str, Any]:
        """Get current time for a specific timezone"""
        try:
            # Get timezone object
            if timezone_str == "UTC":
                tz = timezone.utc
            else:
                tz = pytz.timezone(timezone_str)
            
            # Get current time in the timezone
            now = datetime.now(tz)
            
            return {
                "timezone": timezone_str,
                "location": location or timezone_str,
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "time_12h": now.strftime("%I:%M:%S %p"),
                "date": now.strftime("%A, %B %d, %Y"),
                "utc_offset": now.strftime("%z"),
                "timestamp": now.isoformat()
            }
        
        except Exception as e:
            print(f"Error getting time: {e}")
            return self._get_mock_time_data(timezone_str, location)
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        company_names = {
            "AAPL": "Apple Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc.",
            "AMD": "Advanced Micro Devices Inc.",
            "INTC": "Intel Corporation"
        }
        return company_names.get(symbol.upper(), f"{symbol.upper()} Corp.")
    
    def _get_mock_weather_data(self, location: str) -> Dict[str, Any]:
        """Return mock weather data for testing"""
        import random
        
        return {
            "location": location,
            "country": "US",
            "temperature": round(random.uniform(15, 30), 1),
            "feels_like": round(random.uniform(15, 30), 1),
            "humidity": random.randint(30, 80),
            "pressure": random.randint(1000, 1020),
            "description": random.choice(["clear sky", "few clouds", "scattered clouds", "light rain"]),
            "icon": "01d",
            "wind_speed": round(random.uniform(0, 10), 1),
            "visibility": round(random.uniform(5, 15), 1),
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Return mock stock data for testing"""
        import random
        
        base_price = random.uniform(100, 500)
        change = random.uniform(-10, 10)
        
        return {
            "symbol": symbol.upper(),
            "name": self._get_company_name(symbol),
            "price": round(base_price, 2),
            "change": round(change, 2),
            "change_percent": f"{round((change / base_price) * 100, 2)}%",
            "volume": random.randint(1000000, 10000000),
            "high": round(base_price + random.uniform(0, 5), 2),
            "low": round(base_price - random.uniform(0, 5), 2),
            "open": round(base_price + random.uniform(-2, 2), 2),
            "previous_close": round(base_price - change, 2),
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_news_data(self, query: str) -> Dict[str, Any]:
        """Return mock news data for testing"""
        mock_articles = [
            {
                "title": f"Breaking: {query.title()} makes headlines today",
                "description": f"Latest developments in {query} are capturing global attention.",
                "url": "https://example.com/news1",
                "source": "Mock News",
                "published_at": datetime.now().isoformat(),
                "url_to_image": None
            },
            {
                "title": f"Analysis: The future of {query}",
                "description": f"Experts weigh in on the implications of recent {query} developments.",
                "url": "https://example.com/news2",
                "source": "Mock Analytics",
                "published_at": datetime.now().isoformat(),
                "url_to_image": None
            },
            {
                "title": f"Update: {query.title()} market impact",
                "description": f"How {query} is affecting global markets and industries.",
                "url": "https://example.com/news3",
                "source": "Mock Financial",
                "published_at": datetime.now().isoformat(),
                "url_to_image": None
            }
        ]
        
        return {
            "query": query,
            "total_results": len(mock_articles),
            "articles": mock_articles,
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    def _get_mock_time_data(self, timezone_str: str, location: Optional[str]) -> Dict[str, Any]:
        """Return mock time data for testing"""
        now = datetime.now(timezone.utc)
        
        return {
            "timezone": timezone_str,
            "location": location or timezone_str,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "time_12h": now.strftime("%I:%M:%S %p"),
            "date": now.strftime("%A, %B %d, %Y"),
            "utc_offset": "+0000",
            "timestamp": now.isoformat(),
            "mock": True
        }
