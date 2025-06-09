// src/App.jsx 
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './features/auth/context/AuthContext';
import { AppRouter } from './routes'; // Импортируем наш центральный роутер

const App = () => (
  <AuthProvider>
    <Router>
      <AppRouter />
    </Router>
  </AuthProvider>
);

export default App;