import axios from 'axios';

const BASE_URL = 'https://pearls-aqi.onrender.com';

export const api = {
    getCurrent: () => axios.get(`${BASE_URL}/current`),
    getForecast: (model = 'gradient_boosting') => axios.get(`${BASE_URL}/forecast/${model}`),
    getHistorical: (limit = 500) => axios.get(`${BASE_URL}/historical?limit=${limit}`),
    getModels: () => axios.get(`${BASE_URL}/models`),
    getHealth: () => axios.get(`${BASE_URL}/health`),
};