import axios from 'axios';

export const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Auth interfaces
export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  isVerified: boolean;
  subscription: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: User;
  expiresIn?: number;
}

// Character interfaces
export interface CharacterConfig {
  speed: number;
  nfeSteps: number;
  crossFadeDuration: number;
  removeSilences: boolean;
}

export interface Character {
  id: string;
  displayName: string;
  audioFile?: string;
  config: CharacterConfig;
  images: Record<string, string>;
  outputPrefix: string;
  createdAt: string;
  updatedAt: string;
  hasAudio: boolean;
  imageCount: number;
  createdBy?: string;
  createdByName?: string;
  isOwner: boolean;
  starred: number;
  isStarred: boolean;
}

export interface StarResponse {
  success: boolean;
  message: string;
  characterId: string;
  starred: number;
  isStarred: boolean;
}

// Auth API
export const authAPI = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/signup', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/me');
    return response.data;
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const response = await api.post('/api/refresh-token');
    return response.data;
  },
};

// Script interfaces
export interface ScriptRequest {
  selectedCharacters: string[];
  prompt: string;
  word?: string;
}

export interface DialogueLine {
  speaker: string;
  text: string;
  audioFile?: string;
}

export interface Script {
  id: string;
  selectedCharacters: string[];
  originalPrompt: string;
  word?: string;
  dialogue: DialogueLine[];
  createdAt: string;
  updatedAt: string;
  hasAudio: boolean;
  audioCount: number;
  finalVideoPath?: string;
  videoDuration?: number;
  videoSize?: number;
}

// Character API
export const characterAPI = {
  getAllCharacters: async (): Promise<Character[]> => {
    const response = await api.get('/api/characters');
    return response.data;
  },

  getCharacter: async (characterId: string): Promise<Character> => {
    const response = await api.get(`/api/characters/${characterId}`);
    return response.data;
  },

  getMyCharacters: async (): Promise<Character[]> => {
    const response = await api.get('/api/my-characters');
    return response.data;
  },

  getMyFavorites: async (): Promise<Character[]> => {
    const response = await api.get('/api/my-favorites');
    return response.data;
  },

  starCharacter: async (characterId: string): Promise<StarResponse> => {
    const response = await api.post(`/api/characters/${characterId}/star`);
    return response.data;
  },

  unstarCharacter: async (characterId: string): Promise<StarResponse> => {
    const response = await api.delete(`/api/characters/${characterId}/star`);
    return response.data;
  },

  updateCharacter: async (characterId: string, data: FormData): Promise<Character> => {
    const response = await api.put(`/api/characters/${characterId}`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteCharacter: async (characterId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/api/characters/${characterId}`);
    return response.data;
  },

  createCharacter: async (data: FormData): Promise<Character> => {
    const response = await api.post('/api/characters/complete', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Script API
export const scriptAPI = {
  getMyScripts: async (): Promise<Script[]> => {
    const response = await api.get('/api/my-scripts');
    return response.data;
  },

  getScript: async (scriptId: string): Promise<Script> => {
    const response = await api.get(`/api/scripts/${scriptId}`);
    return response.data;
  },

  createScript: async (data: ScriptRequest): Promise<Script> => {
    const response = await api.post('/api/scripts/generate', data);
    return response.data;
  },

  deleteScript: async (scriptId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/api/scripts/${scriptId}`);
    return response.data;
  },
};

export default api; 