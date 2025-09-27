import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject, takeUntil } from 'rxjs';

import { ChatService } from '../../services/chat.service';
import { ChatSession, Message, ChatRequest } from '../../models/chat.model';
import { MessageComponent } from './message/message.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSidenavModule,
    MatListModule,
    MatDividerModule,
    MatTooltipModule,
    MessageComponent
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messageContainer') messageContainer!: ElementRef;
  @ViewChild('messageInput') messageInput!: ElementRef;

  private destroy$ = new Subject<void>();
  
  // Chat state
  currentMessage = '';
  isLoading = false;
  sessions: ChatSession[] = [];
  messages: Message[] = [];
  currentSession: ChatSession | null = null;
  sidebarOpen = true;

  constructor(
    private chatService: ChatService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadSessions();
    this.subscribeToChatUpdates();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private subscribeToChatUpdates() {
    this.chatService.currentSession$
      .pipe(takeUntil(this.destroy$))
      .subscribe(session => {
        this.currentSession = session;
      });

    this.chatService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
      });
  }

  private loadSessions() {
    this.chatService.getSessions()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (sessions) => {
          this.sessions = sessions;
          if (sessions.length > 0 && !this.currentSession) {
            this.setCurrentSession(sessions[0]);
          }
        },
        error: (error) => {
          console.error('Error loading sessions:', error);
          this.showError('Failed to load chat sessions');
        }
      });
  }

  private scrollToBottom() {
    try {
      if (this.messageContainer) {
        this.messageContainer.nativeElement.scrollTop = this.messageContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      // Ignore scroll errors
    }
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isLoading) {
      return;
    }

    const message = this.currentMessage.trim();
    this.currentMessage = '';
    this.isLoading = true;

    const request: ChatRequest = {
      message,
      session_id: this.currentSession?.id,
      user_id: 'default_user'
    };

    this.chatService.sendMessage(request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          // Message is automatically added to the list via the service
          this.focusInput();
        },
        error: (error) => {
          console.error('Error sending message:', error);
          this.isLoading = false;
          this.showError('Failed to send message');
          this.currentMessage = message; // Restore the message
        }
      });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  createNewSession() {
    const title = prompt('Enter a title for the new chat session:');
    if (title) {
      this.chatService.createSession('default_user', title)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (session) => {
            this.sessions.unshift(session);
            this.setCurrentSession(session);
            this.showSuccess('New chat session created');
          },
          error: (error) => {
            console.error('Error creating session:', error);
            this.showError('Failed to create new session');
          }
        });
    }
  }

  setCurrentSession(session: ChatSession) {
    this.chatService.setCurrentSession(session);
  }

  deleteSession(session: ChatSession, event: Event) {
    event.stopPropagation();
    
    if (confirm(`Are you sure you want to delete "${session.title || 'Untitled'}"?`)) {
      this.chatService.deleteSession(session.id)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.sessions = this.sessions.filter(s => s.id !== session.id);
            if (this.currentSession?.id === session.id) {
              this.setCurrentSession(this.sessions[0] || null);
            }
            this.showSuccess('Chat session deleted');
          },
          error: (error) => {
            console.error('Error deleting session:', error);
            this.showError('Failed to delete session');
          }
        });
    }
  }

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

  private focusInput() {
    setTimeout(() => {
      if (this.messageInput) {
        this.messageInput.nativeElement.focus();
      }
    }, 100);
  }

  private showError(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['error-snackbar']
    });
  }

  private showSuccess(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 2000,
      panelClass: ['success-snackbar']
    });
  }
}
