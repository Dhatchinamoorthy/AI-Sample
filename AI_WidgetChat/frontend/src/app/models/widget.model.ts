export interface WidgetData {
  weather?: WeatherData;
  stock?: StockData;
  news?: NewsData;
  clock?: ClockData;
  top_stocks?: TopStocksData;
}

export interface WeatherData {
  location: {
    name: string;
    country: string;
  };
  current: {
    temperature: number;
    feels_like: number;
    description: string;
    icon: string;
  };
  details: {
    humidity: number;
    pressure: number;
    wind_speed: number;
    visibility: number;
  };
  timestamp: string;
  mock?: boolean;
}

export interface StockData {
  symbol: string;
  company_name: string;
  price: {
    current: number;
    open: number;
    previous_close: number;
  };
  change: {
    amount: number;
    percentage: number;
    is_positive: boolean;
    formatted: string;
  };
  range: {
    high: number;
    low: number;
  };
  volume: number;
  timestamp: string;
  mock?: boolean;
}

export interface NewsData {
  query: string;
  total_results: number;
  articles: NewsArticle[];
  timestamp: string;
  mock?: boolean;
}

export interface NewsArticle {
  title: string;
  description: string;
  url: string;
  source: string;
  published_at: string;
  image_url?: string;
  read_time?: string;
  summary?: string;
}

export interface ClockData {
  timezone: string;
  location: string;
  time: {
    current: string;
    formatted_12h: string;
    formatted_24h: string;
    hour: number;
    hour_12: number;
    minute: number;
    second: number;
    am_pm: string;
  };
  date: {
    full: string;
    day_of_week: string;
    month: string;
    day: string;
    year: string;
  };
  utc_offset: string;
  timestamp: string;
  mock?: boolean;
}

export interface TopStocksData {
  stocks: TopStockItem[];
  total_count: number;
  last_updated: string;
  market: string;
  sort_by: string;
}

export interface TopStockItem {
  symbol: string;
  company_name: string;
  price: {
    current: number;
    open: number;
    previous_close: number;
  };
  change: {
    amount: number;
    percentage: number;
    is_positive: boolean;
    formatted: string;
  };
  volume: number;
  market_cap: number;
  rank: number;
  timestamp: string;
  mock?: boolean;
}

export interface WidgetConfigRequest {
  widget_type: string;
  user_id?: string;
  config: Record<string, any>;
}

export interface WidgetDataRequest {
  widget_type: string;
  params: Record<string, any>;
}

export interface WidgetDataResponse {
  widget_data: any;
  cached: boolean;
  expires_at?: string;
}
