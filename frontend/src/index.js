import React from 'react';
import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App';

import './config/axiosSetup';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
