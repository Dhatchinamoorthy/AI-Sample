from typing import Dict, List, Any, Optional
from datetime import datetime
from app.widgets.base import BaseWidget


class NewsWidget(BaseWidget):
    """News widget implementation"""
    
    def get_widget_type(self) -> str:
        return "news"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "size": "large",
            "theme": "auto",
            "refreshInterval": 600,  # 10 minutes
            "showImages": True,
            "maxArticles": 5,
            "showSource": True,
            "showTimestamp": True,
            "compactView": False
        }
    
    def create_widget_data(self, query: str, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create news widget data"""
        try:
            # Format the news data
            formatted_data = self.format_data(news_data)
            
            # Create widget protocol
            widget_data = {
                "id": f"news_{query.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}",
                "type": "news",
                "title": f"News: {query.title()}",
                "data": formatted_data,
                "config": self.default_config,
                "actions": self.get_supported_actions(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": "newsapi" if not news_data.get("mock") else "mock",
                    "version": "1.0.0"
                }
            }
            
            return widget_data
            
        except Exception as e:
            return self._create_error_widget(f"Failed to create news widget: {str(e)}")
    
    def format_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format news data for display"""
        try:
            articles = raw_data.get("articles", [])
            formatted_articles = []
            
            for article in articles:
                formatted_article = {
                    "title": article.get("title", "No title"),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", "Unknown"),
                    "published_at": article.get("published_at", ""),
                    "image_url": article.get("url_to_image"),
                    "read_time": self._estimate_read_time(article.get("description", "")),
                    "summary": self._create_summary(article.get("description", ""))
                }
                formatted_articles.append(formatted_article)
            
            return {
                "query": raw_data.get("query", ""),
                "total_results": raw_data.get("total_results", 0),
                "articles": formatted_articles,
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
                "mock": raw_data.get("mock", False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _estimate_read_time(self, text: str) -> str:
        """Estimate reading time for an article"""
        if not text:
            return "1 min"
        
        words = len(text.split())
        read_time = max(1, words // 200)  # Average reading speed: 200 words per minute
        
        if read_time == 1:
            return "1 min"
        else:
            return f"{read_time} mins"
    
    def _create_summary(self, description: str, max_length: int = 100) -> str:
        """Create a summary of the article description"""
        if not description:
            return ""
        
        if len(description) <= max_length:
            return description
        
        # Find the last complete sentence within the limit
        truncated = description[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # If period is reasonably close to the end
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate news widget configuration"""
        required_fields = ["size", "theme"]
        optional_fields = ["refreshInterval", "showImages", "maxArticles", "showSource", "showTimestamp", "compactView"]
        
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
        
        # Validate max articles
        if "maxArticles" in config:
            if not isinstance(config["maxArticles"], int) or config["maxArticles"] < 1 or config["maxArticles"] > 20:
                return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        return ["query", "articles"]
    
    def get_optional_fields(self) -> List[str]:
        return ["total_results", "timestamp"]
    
    def get_display_template(self) -> str:
        return "news"
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            self.create_action("refresh"),
            self.create_action("configure"),
            {
                "type": "search",
                "label": "Search News",
                "icon": "search",
                "description": "Search for different news topics"
            },
            {
                "type": "category",
                "label": "Browse Categories",
                "icon": "category",
                "description": "Browse news by category"
            }
        ]
    
    def _create_error_widget(self, error_message: str) -> Dict[str, Any]:
        """Create error widget when data loading fails"""
        return {
            "id": f"news_error_{int(datetime.now().timestamp())}",
            "type": "news",
            "title": "News Widget Error",
            "data": {
                "error": error_message,
                "query": "Error",
                "total_results": 0,
                "articles": [],
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
