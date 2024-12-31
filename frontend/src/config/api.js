export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

export const URLS = {
  CITIES: `${API_BASE_URL}/cities/`,
  EARTHQUAKES: `${API_BASE_URL}/earthquakes/`,
};
