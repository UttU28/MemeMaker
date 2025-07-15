import React, { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { authAPI } from '../services/api';
import type { User, LoginRequest, SignupRequest } from '../services/api';
import { AuthContext } from './AuthContext';
import type { AuthContextType } from './AuthContext';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!token;

  const saveToken = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('authToken', newToken);
  };

  const clearToken = () => {
    setToken(null);
    localStorage.removeItem('authToken');
  };

  const login = async (data: LoginRequest) => {
    try {
      setIsLoading(true);
      const response = await authAPI.login(data);
      
      if (response.success && response.user && response.token) {
        setUser(response.user);
        saveToken(response.token);
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: SignupRequest) => {
    try {
      setIsLoading(true);
      const response = await authAPI.signup(data);
      
      if (response.success && response.user && response.token) {
        setUser(response.user);
        saveToken(response.token);
      } else {
        throw new Error(response.message || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (callback?: () => void) => {
    setUser(null);
    clearToken();
    // Use setTimeout to ensure state updates are processed before callback
    if (callback) {
      setTimeout(callback, 0);
    }
  };

  const refreshUser = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Refresh user error:', error);
      logout();
    }
  };

  const updateUserTokens = (newTokenCount: number) => {
    if (user) {
      setUser({
        ...user,
        tokens: newTokenCount
      });
    }
  };

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Auth initialization error:', error);
          clearToken();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [token]);

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
    refreshUser,
    updateUserTokens,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 