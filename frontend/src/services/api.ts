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
  tokens: number;
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
  dialogue: DialogueLine[];
  createdAt: string;
  updatedAt: string;
  hasAudio: boolean;
  audioCount: number;
  finalVideoPath?: string;
  videoDuration?: number;
  videoSize?: number;
  // Video job information embedded directly in script
  videoJobId?: string;
  videoJobStatus?: 'queued' | 'in_progress' | 'completed' | 'failed';
  videoJobProgress?: number; // 0-100
  videoJobCurrentStep?: string;
  videoJobStartedAt?: string;
  videoJobCompletedAt?: string;
  videoJobErrorMessage?: string;
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

// Script update interface
export interface ScriptUpdate {
  dialogue: DialogueLine[];
}

// My Scripts response interface
export interface MyScriptsResponse {
  scripts: Script[];
  userTokens: number;
}

// Video generation job interfaces
export interface VideoGenerationStep {
  stepName: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message: string;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
}

export interface VideoGenerationJob {
  jobId: string;
  scriptId: string;
  userId: string;
  status: 'queued' | 'in_progress' | 'completed' | 'failed';
  overallProgress: number;
  currentStep: string;
  steps: VideoGenerationStep[];
  totalSteps: number;
  completedSteps: number;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  finalVideoPath?: string;
  videoDuration?: number;
  videoSize?: number;
  errorMessage?: string;
}

export interface VideoGenerationJobResponse {
  job: VideoGenerationJob;
  message: string;
}

// Legacy video status interface (for backward compatibility)
export interface VideoGenerationStatus {
  scriptId: string;
  status: string;
  stage: string;
  progress: number;
  message: string;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
  finalVideoPath?: string;
}

// Audio generation interfaces
export interface AudioGenerationStatus {
  scriptId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial';
  totalLines: number;
  processedLines: number;
  completedLines: number;
  failedLines: number;
}

// User Activity interfaces
export interface UserActivity {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  scriptId?: string;
  characterId?: string;
  videoPath?: string;
}

export interface UserActivityResponse {
  activities: UserActivity[];
  totalCount: number;
  limit: number;
}

export interface ActivityStats {
  scriptActivities: number;
  characterActivities: number;
  videoActivities: number;
  totalActivities: number;
  lastActivityAt?: string;
}

// User Activity API
export const activityAPI = {
  getMyActivities: async (limit: number = 50): Promise<UserActivityResponse> => {
    const response = await api.get<UserActivityResponse>(`/api/my-activities?limit=${limit}`);
    return response.data;
  },

  getMyActivityStats: async (): Promise<ActivityStats> => {
    const response = await api.get<ActivityStats>('/api/my-activity-stats');
    return response.data;
  },

  clearMyActivities: async (): Promise<{ message: string; success: boolean }> => {
    const response = await api.delete('/api/my-activities');
    return response.data;
  },
};

// Script API
export const scriptAPI = {
  createScript: async (scriptRequest: ScriptRequest): Promise<Script> => {
    const response = await api.post<Script>('/api/scripts/generate', scriptRequest);
    return response.data;
  },

  getMyScripts: async (): Promise<MyScriptsResponse> => {
    const response = await api.get<MyScriptsResponse>('/api/my-scripts');
    return response.data;
  },

  getScript: async (scriptId: string): Promise<Script> => {
    const response = await api.get<Script>(`/api/scripts/${scriptId}`);
    return response.data;
  },

  updateScript: async (scriptId: string, updates: ScriptUpdate): Promise<Script> => {
    const response = await api.put<Script>(`/api/scripts/${scriptId}`, updates);
    return response.data;
  },

  deleteScript: async (scriptId: string): Promise<void> => {
    await api.delete(`/api/scripts/${scriptId}`);
  },

  generateVideo: async (scriptId: string, backgroundVideo?: string): Promise<VideoGenerationJobResponse> => {
    const response = await api.post<VideoGenerationJobResponse>(
      `/api/scripts/${scriptId}/generate-video`, 
      backgroundVideo ? { backgroundVideo } : {}
    );
    return response.data;
  },

  getVideoStatus: async (scriptId: string): Promise<VideoGenerationStatus> => {
    const response = await api.get<VideoGenerationStatus>(`/api/scripts/${scriptId}/video-status`);
    return response.data;
  },

  getAudioStatus: async (scriptId: string): Promise<AudioGenerationStatus> => {
    const response = await api.get<AudioGenerationStatus>(`/api/scripts/${scriptId}/audio-status`);
    return response.data;
  },

  // Keep these for backward compatibility or direct job access if needed
  getVideoGenerationJob: async (jobId: string): Promise<VideoGenerationJob> => {
    const response = await api.get<VideoGenerationJob>(`/api/video-jobs/${jobId}`);
    return response.data;
  },

  getMyVideoJobs: async (limit: number = 10): Promise<VideoGenerationJob[]> => {
    const response = await api.get<VideoGenerationJob[]>(`/api/my-video-jobs?limit=${limit}`);
    return response.data;
  },

  getScriptVideoJob: async (scriptId: string): Promise<VideoGenerationJob> => {
    const response = await api.get<VideoGenerationJob>(`/api/scripts/${scriptId}/video-job`);
    return response.data;
  },
};

export default api; 