// routes.ts
import { Routes } from '@angular/router';
import { Loginpage } from './pages/loginpage/loginpage';
import { NotFoundPage } from './pages/not-found-page/not-found-page';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth.guard'; // ⬅️ Importe o Guard

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
  {
    path: 'login',
    component: Loginpage,
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    component: Dashboard,
  },
  {
    path: '**',
    component: NotFoundPage,
  },
];
