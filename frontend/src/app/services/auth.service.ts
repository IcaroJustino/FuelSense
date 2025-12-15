import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { Observable, tap } from 'rxjs';
import { AuthToken, LoginPayload } from '../interfaces/auth.interfaces';
import { Router } from '@angular/router';

const TOKEN_KEY = 'auth_token';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private isBrowser = isPlatformBrowser(this.platformId);

  private apiUrl = 'http://localhost:8000/api/v1';

  public redirectToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }

  // Lógica de Login
  login(payload: LoginPayload): Observable<AuthToken> {
    const body = new URLSearchParams();
    body.set('username', payload.email);
    body.set('password', payload.senha);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http
      .post<AuthToken>(`${this.apiUrl}/auth/token`, body.toString(), { headers: headers })
      .pipe(
        tap((response) => {
          this.saveToken(response.access_token);
          this.redirectToDashboard();
        })
      );
  }

  // Lógica de Logout
  logout() {
    if (this.isBrowser) {
      localStorage.removeItem(TOKEN_KEY);
    }
    this.router.navigate(['/login']);
  }

  // Verifica Autenticação
  isAuthenticated(): boolean {
    if (!this.isBrowser) {
      return false;
    }
    const token = localStorage.getItem(TOKEN_KEY);
    return !!token;
  }

  // Obtém Token
  getToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }
    return localStorage.getItem(TOKEN_KEY);
  }

  private saveToken(token: string) {
    if (this.isBrowser) {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }
}
