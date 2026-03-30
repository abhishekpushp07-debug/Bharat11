/**
 * CrickPredict API Client
 * Centralized API communication with proper error handling
 */
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Create axios instance with defaults
const apiClient = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('crickpredict_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('crickpredict_refresh_token');
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${BACKEND_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('crickpredict_token', access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens
          localStorage.removeItem('crickpredict_token');
          localStorage.removeItem('crickpredict_refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    // Extract error message
    const errorMessage = error.response?.data?.message || error.message || 'Something went wrong';
    const errorCode = error.response?.data?.error || 'UNKNOWN_ERROR';

    return Promise.reject({
      code: errorCode,
      message: errorMessage,
      status: error.response?.status,
      details: error.response?.data?.details || {},
    });
  }
);

// API Methods
export const api = {
  // Health
  health: () => apiClient.get('/health'),

  // Auth
  auth: {
    register: (data) => apiClient.post('/auth/register', data),
    login: (data) => apiClient.post('/auth/login', data),
    refresh: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
    me: () => apiClient.get('/auth/me'),
    changePin: (data) => apiClient.put('/auth/change-pin', data),
    checkPhone: (phone) => apiClient.post('/auth/check-phone', { phone }),
  },

  // User
  user: {
    getProfile: () => apiClient.get('/user/profile'),
    updateProfile: (data) => apiClient.put('/user/profile', data),
    getReferralStats: () => apiClient.get('/user/referral-stats'),
    applyReferral: (code) => apiClient.post('/user/apply-referral', { referral_code: code }),
  },

  // Wallet
  wallet: {
    getBalance: () => apiClient.get('/wallet/balance'),
    getTransactions: (page = 1, limit = 20) => 
      apiClient.get(`/wallet/transactions?page=${page}&limit=${limit}`),
    claimDaily: () => apiClient.post('/wallet/claim-daily'),
  },

  // Matches
  matches: {
    list: (status) => apiClient.get(`/matches${status ? `?status=${status}` : ''}`),
    get: (id) => apiClient.get(`/matches/${id}`),
    getLiveScore: (id) => apiClient.get(`/matches/${id}/live-score`),
    getQuestions: (id) => apiClient.get(`/matches/${id}/questions`),
  },

  // Contests
  contests: {
    listByMatch: (matchId) => apiClient.get(`/matches/${matchId}/contests`),
    get: (id) => apiClient.get(`/contests/${id}`),
    join: (id, teamName) => apiClient.post(`/contests/${id}/join`, { team_name: teamName }),
    getLeaderboard: (id, limit = 50) => 
      apiClient.get(`/contests/${id}/leaderboard?limit=${limit}`),
    getMyEntry: (id) => apiClient.get(`/contests/${id}/my-entry`),
    getUserAnswers: (contestId, userId) => 
      apiClient.get(`/contests/${contestId}/leaderboard/${userId}`),
  },

  // Predictions
  predictions: {
    submit: (data) => apiClient.post('/predictions/submit', data),
    getMy: (contestId) => apiClient.get(`/predictions/my/${contestId}`),
  },

  // My Contests
  myContests: {
    list: (status) => apiClient.get(`/user/my-contests${status ? `?status=${status}` : ''}`),
  },
};

export default apiClient;
