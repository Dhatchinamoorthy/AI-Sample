import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';

import { ChatSession, Message, ChatRequest, ChatResponse } from '../models/chat.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly apiUrl = 'http://localhost:8000/api/v1/chat';
  private currentSessionSubject = new BehaviorSubject<ChatSession | null>(null);
  private messagesSubject = new BehaviorSubject<Message[]>([]);

  public currentSession$ = this.currentSessionSubject.asObservable();
  public messages$ = this.messagesSubject.asObservable();

  constructor(private http: HttpClient) {}

  createSession(userId: string = 'default_user', title?: string): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.apiUrl}/sessions`, {
      user_id: userId,
      title
    }).pipe(
      tap(session => this.currentSessionSubject.next(session))
    );
  }

  getSessions(userId: string = 'default_user'): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>(`${this.apiUrl}/sessions`, {
      params: { user_id: userId }
    });
  }

  getSession(sessionId: number): Observable<ChatSession> {
    return this.http.get<ChatSession>(`${this.apiUrl}/sessions/${sessionId}`).pipe(
      tap(session => this.currentSessionSubject.next(session))
    );
  }

  getSessionMessages(sessionId: number): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/sessions/${sessionId}/messages`).pipe(
      tap(messages => this.messagesSubject.next(messages))
    );
  }

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/message`, request).pipe(
      tap(response => {
        // Update current session
        this.currentSessionSubject.next({
          id: response.session_id,
          user_id: request.user_id,
          title: 'Current Chat',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });

        // Add both user and assistant messages to messages list
        const currentMessages = this.messagesSubject.value;
        const updatedMessages = [...currentMessages, response.user_message, response.assistant_message];
        this.messagesSubject.next(updatedMessages);
      })
    );
  }

  deleteSession(sessionId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/sessions/${sessionId}`);
  }

  setCurrentSession(session: ChatSession | null) {
    this.currentSessionSubject.next(session);
    if (session) {
      this.getSessionMessages(session.id).subscribe();
    } else {
      this.messagesSubject.next([]);
    }
  }

  clearCurrentSession() {
    this.currentSessionSubject.next(null);
    this.messagesSubject.next([]);
  }

  getCurrentSession(): ChatSession | null {
    return this.currentSessionSubject.value;
  }

  getCurrentMessages(): Message[] {
    return this.messagesSubject.value;
  }
}
