import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject, takeUntil } from 'rxjs';

import { Widget } from '../../../models/chat.model';
import { WidgetService } from '../../../services/widget.service';

@Component({
  selector: 'app-widget',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTooltipModule
  ],
  templateUrl: './widget.component.html',
  styleUrl: './widget.component.css'
})
export class WidgetComponent implements OnInit, OnDestroy {
  @Input() widget!: Widget;
  
  private destroy$ = new Subject<void>();
  isLoading = false;
  error: string | null = null;

  constructor(private widgetService: WidgetService) {}

  ngOnInit() {
    // Initialize widget-specific logic if needed
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  get widgetClass(): string {
    return `widget-${this.widget.type}`;
  }

  get sizeClass(): string {
    return `widget-${this.widget.config.size}`;
  }

  onAction(action: any) {
    switch (action.type) {
      case 'refresh':
        this.refreshWidget();
        break;
      case 'configure':
        this.configureWidget();
        break;
      case 'fullscreen':
        this.fullscreenWidget();
        break;
      default:
        console.log('Unknown action:', action);
    }
  }

  private refreshWidget() {
    this.isLoading = true;
    this.error = null;

    this.widgetService.refreshWidgetData(this.widget.id, true)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.isLoading = false;
          // Widget data will be updated by the parent component
        },
        error: (error) => {
          this.isLoading = false;
          this.error = 'Failed to refresh widget';
          console.error('Error refreshing widget:', error);
        }
      });
  }

  private configureWidget() {
    // TODO: Implement widget configuration dialog
    console.log('Configure widget:', this.widget.id);
  }

  private fullscreenWidget() {
    // TODO: Implement fullscreen widget view
    console.log('Fullscreen widget:', this.widget.id);
  }

  getWidgetIcon(): string {
    const icons: { [key: string]: string } = {
      'weather': 'cloud',
      'stock': 'trending_up',
      'news': 'article',
      'clock': 'access_time',
      'top_stocks': 'leaderboard'
    };
    return icons[this.widget.type] || 'widgets';
  }

  getWeatherData() {
    return this.widgetService.extractWeatherData(this.widget);
  }

  getStockData() {
    return this.widgetService.extractStockData(this.widget);
  }

  getNewsData() {
    return this.widgetService.extractNewsData(this.widget);
  }

  getClockData() {
    return this.widgetService.extractClockData(this.widget);
  }

  getTopStocksData() {
    return this.widgetService.extractTopStocksData(this.widget);
  }

  getMaxArticles(): number {
    return this.widget.config['maxArticles'] || 3;
  }

  formatTemperature(temp: number): string {
    return this.widgetService.formatTemperature(temp);
  }

  formatCurrency(amount: number): string {
    return this.widgetService.formatCurrency(amount);
  }

  formatNumber(num: number): string {
    return new Intl.NumberFormat().format(num);
  }

  formatRelativeTime(timestamp: string): string {
    return this.widgetService.formatRelativeTime(timestamp);
  }

  getWeatherIconUrl(iconCode: string): string {
    return this.widgetService.getWeatherIconUrl(iconCode);
  }

  isMockData(): boolean {
    const data = this.getWidgetData();
    return !!(data && data.mock === true);
  }

  private getWidgetData() {
    switch (this.widget.type) {
      case 'weather':
        return this.getWeatherData();
      case 'stock':
        return this.getStockData();
      case 'news':
        return this.getNewsData();
      case 'clock':
        return this.getClockData();
      default:
        return null;
    }
  }
}
