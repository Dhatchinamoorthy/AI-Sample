import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { 
  WidgetConfigRequest, 
  WidgetDataRequest, 
  WidgetDataResponse,
  WidgetData,
  WeatherData,
  StockData,
  NewsData,
  ClockData
} from '../models/widget.model';
import { Widget } from '../models/chat.model';

@Injectable({
  providedIn: 'root'
})
export class WidgetService {
  private readonly apiUrl = 'http://localhost:8000/api/v1/widgets';

  constructor(private http: HttpClient) {}

  getAvailableWidgetTypes(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/types`);
  }

  getWidgetDefaultConfig(widgetType: string): Observable<Record<string, any>> {
    return this.http.get<Record<string, any>>(`${this.apiUrl}/types/${widgetType}/config`);
  }

  validateWidgetConfig(widgetType: string, config: Record<string, any>): Observable<{valid: boolean}> {
    return this.http.post<{valid: boolean}>(`${this.apiUrl}/types/${widgetType}/validate`, config);
  }

  createWidgetConfig(configRequest: WidgetConfigRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/config`, configRequest);
  }

  getWidgetConfigs(userId?: string, widgetType?: string): Observable<any[]> {
    let params: any = {};
    if (userId) params.user_id = userId;
    if (widgetType) params.widget_type = widgetType;
    
    return this.http.get<any[]>(`${this.apiUrl}/config`, { params });
  }

  getWidgetConfig(configId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/config/${configId}`);
  }

  updateWidgetConfig(configId: number, config: Record<string, any>): Observable<any> {
    return this.http.put(`${this.apiUrl}/config/${configId}`, config);
  }

  deleteWidgetConfig(configId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/config/${configId}`);
  }

  getWidgetData(request: WidgetDataRequest): Observable<WidgetDataResponse> {
    return this.http.post<WidgetDataResponse>(`${this.apiUrl}/data`, request);
  }

  refreshWidgetData(widgetId: string, forceRefresh: boolean = false): Observable<any> {
    return this.http.post(`${this.apiUrl}/refresh`, {
      widget_id: widgetId,
      force_refresh: forceRefresh
    });
  }

  clearWidgetCache(widgetType?: string): Observable<any> {
    let params: any = {};
    if (widgetType) params.widget_type = widgetType;
    
    return this.http.delete(`${this.apiUrl}/cache`, { params });
  }

  // Helper methods for creating widget data requests
  createWeatherWidgetData(location: string): WidgetDataRequest {
    return {
      widget_type: 'weather',
      params: { location }
    };
  }

  createStockWidgetData(symbol: string): WidgetDataRequest {
    return {
      widget_type: 'stock',
      params: { symbol }
    };
  }

  createNewsWidgetData(query: string, category?: string): WidgetDataRequest {
    const params: any = { query };
    if (category) params.category = category;
    
    return {
      widget_type: 'news',
      params
    };
  }

  createClockWidgetData(timezone: string, location?: string): WidgetDataRequest {
    const params: any = { timezone };
    if (location) params.location = location;
    
    return {
      widget_type: 'clock',
      params
    };
  }

  // Helper methods for extracting specific data types
  extractWeatherData(widget: Widget): WeatherData | null {
    return widget?.data as WeatherData || null;
  }

  extractStockData(widget: Widget): StockData | null {
    return widget?.data as StockData || null;
  }

  extractNewsData(widget: Widget): NewsData | null {
    return widget?.data as NewsData || null;
  }

  extractClockData(widget: Widget): ClockData | null {
    return widget?.data as ClockData || null;
  }

  // Utility methods
  formatTemperature(temp: number, unit: 'celsius' | 'fahrenheit' = 'celsius'): string {
    if (unit === 'fahrenheit') {
      const fahrenheit = (temp * 9/5) + 32;
      return `${fahrenheit.toFixed(1)}°F`;
    }
    return `${temp.toFixed(1)}°C`;
  }

  formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  }

  formatPercentage(value: number): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  formatRelativeTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  }

  getWeatherIconUrl(iconCode: string): string {
    return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
  }
}
