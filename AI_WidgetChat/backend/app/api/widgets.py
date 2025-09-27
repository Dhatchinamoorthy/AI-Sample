from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database import get_db
from app.models.widget import WidgetConfig, WidgetCache
from app.services.widget_service import WidgetService
from app.services.external_apis import ExternalAPIService

router = APIRouter()

# Pydantic models for request/response
class WidgetConfigCreate(BaseModel):
    widget_type: str
    user_id: Optional[str] = None
    config: Dict[str, Any]

class WidgetConfigResponse(BaseModel):
    id: int
    widget_type: str
    user_id: Optional[str]
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WidgetDataRequest(BaseModel):
    widget_type: str
    params: Dict[str, Any]

class WidgetDataResponse(BaseModel):
    widget_data: Dict[str, Any]
    cached: bool = False
    expires_at: Optional[datetime] = None

class WidgetRefreshRequest(BaseModel):
    widget_id: str
    force_refresh: bool = False


@router.get("/types", response_model=List[str])
async def get_available_widget_types():
    """Get list of available widget types"""
    widget_service = WidgetService()
    return widget_service.get_available_widget_types()


@router.get("/types/{widget_type}/config", response_model=Dict[str, Any])
async def get_widget_default_config(widget_type: str):
    """Get default configuration for a widget type"""
    widget_service = WidgetService()
    config = widget_service.get_widget_default_config(widget_type)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Widget type '{widget_type}' not found"
        )
    
    return config


@router.post("/types/{widget_type}/validate", response_model=Dict[str, bool])
async def validate_widget_config(widget_type: str, config: Dict[str, Any]):
    """Validate widget configuration"""
    widget_service = WidgetService()
    is_valid = widget_service.validate_widget_config(widget_type, config)
    
    return {"valid": is_valid}


@router.post("/config", response_model=WidgetConfigResponse)
async def create_widget_config(
    config_data: WidgetConfigCreate,
    db: Session = Depends(get_db)
):
    """Create a new widget configuration"""
    widget_service = WidgetService()
    
    # Validate the configuration
    if not widget_service.validate_widget_config(config_data.widget_type, config_data.config):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid widget configuration"
        )
    
    # Create widget config in database
    db_config = WidgetConfig(
        widget_type=config_data.widget_type,
        user_id=config_data.user_id,
        config=config_data.config
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/config", response_model=List[WidgetConfigResponse])
async def get_widget_configs(
    user_id: Optional[str] = Query(None),
    widget_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get widget configurations with optional filters"""
    query = db.query(WidgetConfig)
    
    if user_id:
        query = query.filter(WidgetConfig.user_id == user_id)
    
    if widget_type:
        query = query.filter(WidgetConfig.widget_type == widget_type)
    
    configs = query.order_by(WidgetConfig.updated_at.desc()).all()
    return configs


@router.get("/config/{config_id}", response_model=WidgetConfigResponse)
async def get_widget_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific widget configuration"""
    config = db.query(WidgetConfig).filter(WidgetConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget configuration not found"
        )
    
    return config


@router.put("/config/{config_id}", response_model=WidgetConfigResponse)
async def update_widget_config(
    config_id: int,
    config_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update a widget configuration"""
    config = db.query(WidgetConfig).filter(WidgetConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget configuration not found"
        )
    
    widget_service = WidgetService()
    
    # Validate the new configuration
    if not widget_service.validate_widget_config(config.widget_type, config_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid widget configuration"
        )
    
    config.config = config_data
    config.updated_at = datetime.now()
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/config/{config_id}")
async def delete_widget_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Delete a widget configuration"""
    config = db.query(WidgetConfig).filter(WidgetConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return {"message": "Widget configuration deleted successfully"}


@router.post("/data", response_model=WidgetDataResponse)
async def get_widget_data(
    request: WidgetDataRequest,
    db: Session = Depends(get_db)
):
    """Get widget data, using cache if available"""
    widget_service = WidgetService()
    external_api_service = ExternalAPIService()
    
    # Generate cache key
    cache_key = f"{request.widget_type}:{hash(str(request.params))}"
    
    # Check cache first
    cached_data = db.query(WidgetCache).filter(
        WidgetCache.widget_type == request.widget_type,
        WidgetCache.cache_key == cache_key,
        WidgetCache.expires_at > datetime.now()
    ).first()
    
    if cached_data:
        return WidgetDataResponse(
            widget_data=cached_data.data,
            cached=True,
            expires_at=cached_data.expires_at
        )
    
    # Generate new data
    try:
        widget_data = await _generate_widget_data(
            request.widget_type, 
            request.params, 
            widget_service, 
            external_api_service
        )
        
        # Cache the data
        expires_at = datetime.now() + timedelta(seconds=widget_service.get_widget_refresh_interval(request.widget_type))
        
        cache_entry = WidgetCache(
            widget_type=request.widget_type,
            cache_key=cache_key,
            data=widget_data,
            expires_at=expires_at
        )
        
        db.add(cache_entry)
        db.commit()
        
        return WidgetDataResponse(
            widget_data=widget_data,
            cached=False,
            expires_at=expires_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating widget data: {str(e)}"
        )


@router.post("/refresh")
async def refresh_widget_data(
    request: WidgetRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh widget data, bypassing cache if force_refresh is True"""
    if request.force_refresh:
        # Clear cache for this widget
        db.query(WidgetCache).filter(
            WidgetCache.widget_type == request.widget_type
        ).delete()
        db.commit()
    
    # The client should then call the /data endpoint to get fresh data
    return {"message": "Widget refresh requested"}


@router.delete("/cache")
async def clear_widget_cache(
    widget_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Clear widget cache"""
    query = db.query(WidgetCache)
    
    if widget_type:
        query = query.filter(WidgetCache.widget_type == widget_type)
    
    deleted_count = query.delete()
    db.commit()
    
    return {"message": f"Cleared {deleted_count} cache entries"}


async def _generate_widget_data(
    widget_type: str,
    params: Dict[str, Any],
    widget_service: WidgetService,
    external_api_service: ExternalAPIService
) -> Dict[str, Any]:
    """Generate widget data based on type and parameters"""
    
    if widget_type == "weather":
        location = params.get("location", "New York")
        weather_data = await external_api_service.get_weather(location)
        return widget_service.create_weather_widget(location, weather_data)
    
    elif widget_type == "stock":
        symbol = params.get("symbol", "AAPL")
        stock_data = await external_api_service.get_stock_price(symbol)
        return widget_service.create_stock_widget(symbol, stock_data)
    
    elif widget_type == "news":
        query = params.get("query", "technology")
        category = params.get("category")
        news_data = await external_api_service.get_news(query, category)
        return widget_service.create_news_widget(query, news_data)
    
    elif widget_type == "clock":
        timezone = params.get("timezone", "UTC")
        location = params.get("location")
        time_data = await external_api_service.get_time(timezone, location)
        return widget_service.create_clock_widget(timezone, location, time_data)
    
    elif widget_type == "top_stocks":
        limit = params.get("limit", 10)
        stocks_data = await external_api_service.get_top_stocks(limit)
        return widget_service.create_top_stocks_widget(stocks_data)
    
    else:
        raise ValueError(f"Unknown widget type: {widget_type}")
