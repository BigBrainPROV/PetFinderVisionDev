import axios from 'axios';

const searchApi = axios.create({
    baseURL: 'http://localhost:5004',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for logging
searchApi.interceptors.request.use(
    (config) => {
        console.log('Search API Request:', {
            url: config.url,
            method: config.method,
            headers: config.headers,
        });
        return config;
    },
    (error) => {
        console.error('Search API Request Error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for logging
searchApi.interceptors.response.use(
    (response) => {
        console.log('Search API Response:', {
            status: response.status,
            data: response.data,
        });
        return response;
    },
    (error) => {
        console.error('Search API Response Error:', error);
        return Promise.reject(error);
    }
);

export default searchApi; 