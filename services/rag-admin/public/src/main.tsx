// file: src/main.tsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '@/app/App'; 
import '@/app/styles/global.css';

// 1. Ensure the root element exists before trying to render the app. This prevents runtime errors if 
// the 'root' element is missing in index.html.
const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error(
    "TGramLLM-Frontend: Fatal Error. The root element with ID 'root' was not found in the DOM. The application cannot be mounted."
  );
}

// 2. Create the root only once and render the application. React.StrictMode will
//    identify potential problems in an application and activates additional checks and warnings for its descendants.
const root = createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);