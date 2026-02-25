import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Paper endpoints
export const paperAPI = {
  generatePaper: (request) => 
    apiClient.post('/papers/generate', request),
  
  getPaperStatus: (paperId) => 
    apiClient.get(`/papers/status/${paperId}`),
  
  getPaper: (paperId) => 
    apiClient.get(`/papers/${paperId}`),

  listUserPapers: (userId) =>
    apiClient.get(`/papers/user/${userId}`),

  getPaperContent: (paperId) =>
    apiClient.get(`/papers/${paperId}/content`),

  downloadPaperWord: (paperId) =>
    axios.get(`${API_BASE_URL}/papers/${paperId}/download`, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
    }),
};

// User endpoints
export const userAPI = {
  registerUser: (userData) => 
    apiClient.post('/users/register', userData),
  
  getUserProfile: (userId) => 
    apiClient.get(`/users/${userId}`),
};

export default apiClient;
