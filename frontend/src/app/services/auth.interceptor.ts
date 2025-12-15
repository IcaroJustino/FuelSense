import { HttpInterceptorFn, HttpHeaders } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const authToken = authService.getToken();

  if (req.url.includes('/auth/token')) {
    return next(req);
  }

  if (authToken) {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${authToken}`,
    });

    const authReq = req.clone({
      headers: headers,
    });

    return next(authReq);
  }

  return next(req);
};
