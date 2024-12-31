import axios from 'axios';

// Set up axios defaults for CSRF
axios.defaults.xsrfCookieName = 'csrftoken';   // Django's default cookie name
axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // The header Django looks for
axios.defaults.withCredentials = true;         // Send cookies in cross-site requests if needed

export default axios; // Export this axios instance
