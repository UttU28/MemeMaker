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
      window.location.href = '/';
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

// Admin Dashboard interfaces
export interface SystemStatus {
  status: string;
  totalCharacters: number;
  timestamp: string;
  apiDataDir: string;
}

export interface ServiceStatus {
  status: string;
  url?: string;
  message?: string;
  timestamp: string;
  error?: string;
}

export interface VideoQueueStatus {
  queue_size: number;
  is_processing: boolean;
  current_job_id: string | null;
  processing_jobs_count: number;
  active_jobs: string[];
  active_jobs_details: Array<{
    jobId: string;
    scriptId: string;
    status: string;
    currentStep: string;
    overallProgress: number;
    createdAt: string;
  }>;
  message: string;
}

export interface AdminStats {
  totalUsers: number;
  totalCharacters: number;
  totalScripts: number;
  totalVideos: number;
  totalTokens: number;
  tokensUsedToday: number;
  newUsersToday: number;
  charactersCreatedToday: number;
  scriptsGeneratedToday: number;
  videosCreatedToday: number;
  topTokenUser: {
    name: string;
    email: string;
    tokens: number;
  } | null;
  averageTokensPerUser: number;
}

export interface RecentUser {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  tokens: number;
  lastActivity?: string;
}

export interface SystemAlert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high';
}

export interface UserFeedback {
  userName: string;
  userEmail: string;
  message: string;
  timestamp: string;
  isRead: boolean;
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
  signup: (data: SignupRequest): Promise<AuthResponse> =>
    api.post('/api/signup', data).then(res => res.data),
  
  login: (data: LoginRequest): Promise<AuthResponse> =>
    api.post('/api/login', data).then(res => res.data),
  
  getCurrentUser: (): Promise<User> =>
    api.get('/api/me').then(res => res.data),
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

  // New combined endpoint to reduce API calls
  getCharactersCombined: async (): Promise<{
    all: Character[];
    my_characters: Character[];
    my_favorites: Character[];
  }> => {
    const response = await api.get('/api/characters-combined');
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

  // New combined endpoint to reduce API calls
  getMyActivitiesCombined: async (limit: number = 50): Promise<{
    activities: UserActivity[];
    stats: ActivityStats;
  }> => {
    const response = await api.get(`/api/my-activities-combined?limit=${limit}`);
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

// Feedback API
export const feedbackAPI = {
  submitFeedback: async (message: string): Promise<{ success: boolean; message: string; feedbackId?: string }> => {
    const response = await api.post('/api/feedback', { message });
    return response.data;
  },
};

// Admin API functions
export const adminAPI = {
  // System Status
  getSystemStatus: (): Promise<SystemStatus> =>
    api.get('/api/system/status').then(res => res.data),
  
  getF5TTSStatus: (): Promise<ServiceStatus> =>
    api.get('/api/f5tts/status').then(res => res.data),
  
  getFFmpegStatus: (): Promise<ServiceStatus> =>
    api.get('/api/system/ffmpeg-status').then(res => res.data),
  
  // Statistics
  getAdminStats: (): Promise<AdminStats> =>
    api.get('/api/admin/stats').then(res => res.data),
  
  // Video Queue
  getVideoQueueStatus: (): Promise<VideoQueueStatus> =>
    api.get('/api/video-queue/status').then(res => res.data),
  
  // Recent Users
  getRecentUsers: (limit: number = 10): Promise<RecentUser[]> =>
    api.get(`/api/admin/recent-users?limit=${limit}`).then(res => res.data),
  
  // System Alerts
  getSystemAlerts: (limit: number = 10): Promise<SystemAlert[]> =>
    api.get(`/api/admin/alerts?limit=${limit}`).then(res => res.data),
  
  // User Feedback
  getUserFeedback: (limit: number = 50): Promise<UserFeedback[]> =>
    api.get(`/api/admin/feedback?limit=${limit}`).then(res => res.data),
  
  markFeedbackAsRead: (feedbackId: string): Promise<{ success: boolean; message: string }> =>
    api.put(`/api/admin/feedback/${feedbackId}/mark-read`).then(res => res.data),
  
  // System Actions
  restartServices: (): Promise<{ success: boolean; message: string }> =>
    api.post('/api/admin/restart-services').then(res => res.data),
  
  clearCache: (): Promise<{ success: boolean; message: string }> =>
    api.post('/api/admin/clear-cache').then(res => res.data),
  
  exportData: (type: 'users' | 'characters' | 'scripts' | 'videos' = 'users'): Promise<Blob> =>
    api.get(`/api/admin/export/${type}`, { responseType: 'blob' }).then(res => res.data),
  
  sendAlert: (message: string, type: 'info' | 'warning' | 'error' = 'info'): Promise<{ success: boolean; message: string }> =>
    api.post('/api/admin/send-alert', { message, type }).then(res => res.data),
};

export default api; 