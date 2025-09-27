export interface ChatSession {
  id: number;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  session_id: number;
  content: string;
  role: 'user' | 'assistant';
  widgets?: Widget[];
  created_at: string;
}

export interface ChatRequest {
  message: string;
  session_id?: number;
  user_id: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
  session_id: number;
  widgets?: Widget[];
}

export interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  data: any;
  config: WidgetConfig;
  actions?: WidgetAction[];
  metadata?: WidgetMetadata;
}

export interface WidgetConfig {
  size: 'small' | 'medium' | 'large';
  theme: 'light' | 'dark' | 'auto';
  refreshInterval?: number;
  [key: string]: any;
}

export interface WidgetAction {
  type: string;
  label: string;
  icon?: string;
  description?: string;
  [key: string]: any;
}

export interface WidgetMetadata {
  created_at: string;
  updated_at: string;
  source: string;
  version: string;
}

export type WidgetType = 'weather' | 'stock' | 'news' | 'clock' | 'custom';
