import axios from 'axios';

// API base URL - change this to the appropriate URL for your environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload endpoints
export const uploadChatLog = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return api.post('/upload/chat', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const uploadPdf = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return api.post('/upload/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const checkUploadStatus = async (filename) => {
  return api.get(`/upload/status/${filename}`);
};

// Email endpoints
export const fetchEmails = async (addresses, startDate, endDate) => {
  return api.post('/emails/fetch', {
    addresses: addresses.map(address => ({ address })),
    start_date: startDate,
    end_date: endDate,
  });
};

export const getEmails = async (params = {}) => {
  return api.get('/emails', { params });
};

export const getEmailById = async (id) => {
  return api.get(`/emails/${id}`);
};

export const getEmailStatus = async () => {
  return api.get('/emails/status');
};

// Search endpoints
export const searchData = async (params = {}) => {
  return api.get('/search', { params });
};

// Timeline endpoints
export const generateTimeline = async (params = {}) => {
  return api.post('/timeline/generate', params);
};

export const getTimelineById = async (id) => {
  return api.get(`/timeline/${id}`);
};

export const getTimelines = async () => {
  return api.get('/timelines');
};

export const deleteTimeline = async (id) => {
  return api.delete(`/timeline/${id}`);
};

// Evidence endpoints
export const analyzeEvidence = async () => {
  return api.post('/evidence/analyze');
};

export const getEvidence = async () => {
  return api.get('/evidence');
};

export const getEvidenceById = async (id) => {
  return api.get(`/evidence/${id}`);
};

export const getEvidenceSource = async (sourceType, sourceId) => {
  return api.get(`/evidence/source/${sourceType}/${sourceId}`);
};

export const deleteEvidence = async (id) => {
  return api.delete(`/evidence/${id}`);
};

// Report endpoints
export const generateReport = async (timelineId, title) => {
  return api.post('/report/generate', { timeline_id: timelineId, title });
};

export const getReportById = async (id) => {
  return api.get(`/report/${id}`);
};

export const getReports = async () => {
  return api.get('/reports');
};

export const deleteReport = async (id) => {
  return api.delete(`/report/${id}`);
};

export default api;