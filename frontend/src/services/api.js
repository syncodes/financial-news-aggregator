import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = {
  getNews: async (params = {}) => {
    try {
      const response = await axios.get(`${API_URL}/api/news`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching news:', error);
      throw error;
    }
  },
  
  getSources: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/news/sources`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sources:', error);
      throw error;
    }
  },
  
  getStats: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/news/stats`);
      return response.data;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  }
};

export default api;
