import axios from 'axios';

// Supports both unified hosting (/api) and separate frontend/backend deployments (VITE_API_URL)
const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    const raw = import.meta.env.VITE_API_URL.trim().replace(/\/$/, '');
    return raw.endsWith('/api') ? raw : `${raw}/api`;
  }
  return '/api';
};

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = () => api.get('/health').then(r => r.data);
export const getSettings = () => api.get('/settings').then(r => r.data);
export const updateSettings = (data) => api.post('/settings', data).then(r => r.data);
export const preloadSamples = () => api.post('/preload-samples').then(r => r.data);

// Resumes
export const getResumes = () => api.get('/resumes').then(r => r.data);
export const getResume = (id) => api.get(`/resumes/${id}`).then(r => r.data);
export const deleteResume = (id) => api.delete(`/resumes/${id}`).then(r => r.data);
export const uploadResumes = (formData) => api.post('/resumes/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
}).then(r => r.data);

// Jobs
export const getJobs = () => api.get('/jobs').then(r => r.data);
export const getJob = (id) => api.get(`/jobs/${id}`).then(r => r.data);
export const createJob = (data) => api.post('/jobs', data).then(r => r.data);
export const deleteJob = (id) => api.delete(`/jobs/${id}`).then(r => r.data);

// Agent
export const queryAgent = (data) => api.post('/agent/query', data).then(r => r.data);
export const rankCandidates = (jobId) => api.post(`/agent/rank/${jobId}`).then(r => r.data);
export const getRanking = (jobId) => api.get(`/agent/ranking/${jobId}`).then(r => r.data);
export const getScorecard = (candidateId, jobId) => api.get(`/agent/scorecard/${candidateId}/${jobId}`).then(r => r.data);

export default api;
