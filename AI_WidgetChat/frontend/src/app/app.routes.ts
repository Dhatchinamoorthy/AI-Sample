import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/chat',
    pathMatch: 'full'
  },
  {
    path: 'chat',
    loadComponent: () => import('./components/chat/chat.component').then(m => m.ChatComponent)
  },
  {
    path: 'widgets',
    loadComponent: () => import('./components/widgets/widgets.component').then(m => m.WidgetsComponent)
  },
  {
    path: 'settings',
    loadComponent: () => import('./components/settings/settings.component').then(m => m.SettingsComponent)
  },
  {
    path: '**',
    redirectTo: '/chat'
  }
];