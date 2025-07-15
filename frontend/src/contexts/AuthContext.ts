import { createContext } from 'react';
import type { User, LoginRequest, SignupRequest } from '../services/api';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: (callback?: () => void) => void;
  refreshUser: () => Promise<void>;
  updateUserTokens: (newTokenCount: number) => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined); 