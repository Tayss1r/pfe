'use client';

/**
 * Authentication Context and Hook
 *
 * Provides authentication state and methods throughout the app
 * Implements silent refresh on mount
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService, UserData, LoginData, RegisterData } from '@/lib/auth-service';
import { clearAccessToken } from '@/lib/api-client';

interface AuthContextType {
  user: UserData | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<{ email: string }>;
  logout: () => Promise<void>;
  verifyEmail: (email: string, code: string) => Promise<void>;
  resendVerificationCode: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Silent refresh on app initialization
  useEffect(() => {
    const initAuth = async () => {
      try {
        const userData = await authService.silentRefresh();
        if (userData) {
          setUser(userData);
        }
      } catch (error) {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (data: LoginData) => {
    setIsLoading(true);
    try {
      const { user: userData } = await authService.login(data);
      setUser(userData);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    setIsLoading(true);
    try {
      const response = await authService.register(data);
      return { email: response.email };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      clearAccessToken();
      setIsLoading(false);
    }
  };

  const verifyEmail = async (email: string, code: string) => {
    await authService.verifyEmail(email, code);
  };

  const resendVerificationCode = async (email: string) => {
    await authService.resendVerificationCode(email);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        register,
        logout,
        verifyEmail,
        resendVerificationCode,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

