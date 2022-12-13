import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { ProjectContextProvider } from './context/projectContext';

import 'bootswatch/dist/pulse/bootstrap.min.css'
import { AuthContextProvider } from './context/AuthContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AuthContextProvider>
      <ProjectContextProvider>
        <App />
      </ProjectContextProvider>
    </AuthContextProvider>
  </React.StrictMode>
);
