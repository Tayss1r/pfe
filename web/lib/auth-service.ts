/**
 * Authentication Service
 *
 * Handles login, registration, logout, and silent refresh
 */

import { apiClient, setAccessToken, clearAccessToken } from './api-client';

export interface RegisterData {
  email: string;
  password: string;
  username: string;
  fullname: string;
  role?: 'technicien' | 'admin';
}

export interface LoginData {
  email: string;
  password: string;
}

export interface UserData {
  email: string;
  uid: string;
  role: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  user: UserData;
}

export interface RegisterResponse {
  message: string;
  email: string;
}

class AuthService {
  /**
   * Register a new user
   * POST /auth/signup
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>('/auth/signup', data);
    return response.data;
  }

  /**
   * Login user
   * POST /auth/login
   *
   * Backend sets refresh_token in HttpOnly cookie
   * We store access_token in memory
   */
  async login(data: LoginData): Promise<{ user: UserData }> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data);

    // Store access token in memory
    setAccessToken(response.data.access_token);

    return { user: response.data.user };
  }

  /**
   * Logout user
   * GET /auth/logout
   *
   * Clears access token from memory and refresh token cookie from backend
   */
  async logout(): Promise<void> {
    try {
      await apiClient.get('/auth/logout');
    } finally {
      // Always clear local access token even if logout request fails
      clearAccessToken();
    }
  }

  /**
   * Silent refresh - attempt to get new access token using refresh token cookie
   * GET /auth/refresh_token
   *
   * Call this on app initialization to restore session
   * Returns user data if successful, null if not authenticated
   */
  async silentRefresh(): Promise<UserData | null> {
    try {
      const response = await apiClient.get<{ access_token: string }>('/auth/refresh_token');

      // Store new access token
      setAccessToken(response.data.access_token);

      // Decode JWT to get user data (simple base64 decode, no verification needed)
      const payload = this.decodeJWT(response.data.access_token);

      if (payload && payload.user) {
        return {
          email: payload.user.email,
          uid: payload.user.user_uid,
          role: payload.user.role,
        };
      }

      return null;
    } catch (error) {
      // No valid refresh token - user is not authenticated
      clearAccessToken();
      return null;
    }
  }

  /**
   * Verify email with 6-digit code
   * POST /auth/verify-email-code
   */
  async verifyEmail(email: string, code: string): Promise<void> {
    await apiClient.post('/auth/verify-email-code', { email, code });
  }

  /**
   * Resend verification code
   * POST /auth/send-verification-code
   */
  async resendVerificationCode(email: string): Promise<void> {
    await apiClient.post('/auth/send-verification-code', { email });
  }

  /**
   * Decode JWT token (client-side, for reading user data only)
   * NOT for validation - backend validates tokens
   */
  private decodeJWT(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      return null;
    }
  }
}

export const authService = new AuthService();

