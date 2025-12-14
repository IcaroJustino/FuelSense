import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { LoginPayload } from '../../interfaces/auth.interfaces';

export interface Toast {
  message: string;
  type: 'success' | 'error';
}

@Component({
  selector: 'app-loginpage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './loginpage.html',
})
export class Loginpage {
  private authService = inject(AuthService);

  credentials: LoginPayload = {
    email: '',
    senha: '',
  };

  isLoading = signal(false);
  showPassword = signal(false);
  hasError = signal(false);
  toast = signal<Toast | null>(null);

  constructor() {
    if (this.authService.isAuthenticated()) {
      this.authService.redirectToDashboard();
    }
  }

  onLogin() {
    this.hasError.set(false);
    this.isLoading.set(true);
    this.toast.set(null);

    this.authService.login(this.credentials).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.showToast({ message: 'Login realizado com sucesso!', type: 'success' });
      },
      error: (err) => {
        this.isLoading.set(false);
        this.hasError.set(true);

        let msg = 'Falha na autenticação. Verifique suas credenciais.';
        if (err.status === 401 || err.status === 403) {
          msg = 'Credenciais inválidas. Tente novamente.';
        }

        this.showToast({ message: msg, type: 'error' });
      },
    });
  }

  togglePasswordVisibility() {
    this.showPassword.set(!this.showPassword());
  }

  showToast(t: Toast) {
    this.toast.set(t);
    setTimeout(() => {
      this.toast.set(null);
    }, 4000);
  }
}
