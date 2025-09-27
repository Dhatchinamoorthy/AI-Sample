import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';

import { Message } from '../../../models/chat.model';
import { WidgetComponent } from '../../widgets/widget/widget.component';

@Component({
  selector: 'app-message',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatChipsModule,
    MatButtonModule,
    WidgetComponent
  ],
  templateUrl: './message.component.html',
  styleUrl: './message.component.css'
})
export class MessageComponent {
  @Input() message!: Message;

  get isUser(): boolean {
    return this.message.role === 'user';
  }

  get isAssistant(): boolean {
    return this.message.role === 'assistant';
  }

  get hasWidgets(): boolean {
    return !!(this.message.widgets && this.message.widgets.length > 0);
  }

  get formattedTime(): string {
    return new Date(this.message.created_at).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
