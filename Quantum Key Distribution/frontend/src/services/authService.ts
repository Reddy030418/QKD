import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
}

class AuthService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Login user
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await this.api.post('/auth/login', credentials);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.error || 'Login failed');
      }
      throw new Error('Network error occurred');
    }
  }

  // Register user
  async register(userData: RegisterRequest): Promise<{ message: string; user_id: number; username: string }> {
    try {
      const response = await this.api.post('/auth/register', userData);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.error || 'Registration failed');
      }
      throw new Error('Network error occurred');
    }
  }

  // Get current user
  async getCurrentUser(token: string): Promise<User> {
    try {
      const response = await this.api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.error || 'Failed to get user info');
      }
      throw new Error('Network error occurred');
    }
  }

  // Logout (client-side only)
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    return !!token;
  }

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // Store token and user info
  setAuthData(authData: AuthResponse): void {
    localStorage.setItem('auth_token', authData.access_token);
    localStorage.setItem('user_info', JSON.stringify({
      user_id: authData.user_id,
      username: authData.username,
    }));
  }

  // Get stored user info
  getUserInfo(): { user_id: number; username: string } | null {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }
}

export const authService = new AuthService();
