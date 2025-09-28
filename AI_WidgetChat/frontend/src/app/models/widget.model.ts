export interface WidgetData {
  weather?: WeatherData;
  stock?: StockData;
  news?: NewsData;
  clock?: ClockData;
  top_stocks?: TopStocksData;
  // Banking data interfaces
  banking_accounts?: BankingAccountsData;
  banking_transactions?: BankingTransactionsData;
  banking_offers?: BankingOffersData;
  banking_payments?: BankingPaymentsData;
  banking_banker?: BankingBankerData;
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
  mock?: boolean;
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

// Banking data interfaces
export interface BankingAccountsData {
  accounts: BankingAccount[];
  summary: {
    total_accounts: number;
    active_accounts: number;
    total_balance: number;
    total_balance_formatted: string;
    account_types: string[];
  };
  timestamp: string;
  mock?: boolean;
}

export interface BankingAccount {
  id: string;
  account_number: string;
  name: string;
  type: string;
  balance: number;
  balance_formatted: string;
  currency: string;
  status: string;
  last_activity: string;
  last_activity_formatted: string;
  is_positive: boolean;
}

export interface BankingTransactionsData {
  account_id: string;
  transactions: BankingTransaction[];
  summary: {
    total_transactions: number;
    account_balance: number;
    account_balance_formatted: string;
    total_debits: number;
    total_debits_formatted: string;
    total_credits: number;
    total_credits_formatted: string;
  };
  timestamp: string;
  mock?: boolean;
}

export interface BankingTransaction {
  id: string;
  type: string;
  amount: number;
  amount_formatted: string;
  is_debit: boolean;
  description: string;
  merchant: string;
  date: string;
  date_formatted: string;
  status: string;
  category: string;
  reference: string;
}

export interface BankingOffersData {
  offers: BankingOffer[];
  summary: {
    total_offers: number;
    active_offers: number;
    expired_offers: number;
    categories: string[];
  };
  timestamp: string;
  mock?: boolean;
}

export interface BankingOffer {
  id: string;
  title: string;
  description: string;
  category: string;
  type: string;
  value: string;
  valid_until: string;
  valid_until_formatted: string;
  requirements: string;
  status: string;
  is_expired: boolean;
  days_remaining: number;
  priority: number;
}

export interface BankingPaymentsData {
  payment_type: string;
  payment_methods: BankingPaymentMethod[];
  context: {
    amount?: number;
    amount_formatted?: string;
    recipient?: string;
  };
  summary: {
    total_methods: number;
    free_methods: number;
    instant_methods: number;
    available_types: string[];
  };
  timestamp: string;
  mock?: boolean;
}

export interface BankingPaymentMethod {
  id: string;
  type: string;
  name: string;
  description: string;
  url: string;
  fee: number;
  fee_formatted: string;
  processing_time: string;
  is_free: boolean;
  is_instant: boolean;
  recommended: boolean;
}

export interface BankingBankerData {
  bankers: BankingBanker[];
  summary: {
    total_bankers: number;
    available_bankers: number;
    departments: string[];
    specializations: string[];
  };
  timestamp: string;
  mock?: boolean;
}

export interface BankingBanker {
  id: string;
  name: string;
  title: string;
  department: string;
  specialization: string;
  email: string;
  phone: string;
  availability: string;
  experience: string;
  experience_years: number;
  languages: string[];
  is_available: boolean;
  contact_methods: string[];
  expertise_level: string;
}
