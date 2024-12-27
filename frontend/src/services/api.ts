import axios from 'axios';
import { Project, ProjectProgress, Feature } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const projectApi = {
    initialize: async (project: Project) => {
        const response = await api.post('/init', project);
        return response.data;
    },

    submitFeedback: async (feedback: { features?: Feature[], objectives?: string[] }) => {
        const response = await api.post('/feedback', feedback);
        return response.data;
    },

    getProgress: async (): Promise<ProjectProgress> => {
        const response = await api.get('/progress');
        return response.data;
    },

    downloadPRD: async () => {
        const response = await api.get('/download');
        return response.data;
    },
}; 