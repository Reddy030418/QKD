import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styled, { createGlobalStyle } from 'styled-components';

// Components
import Header from './components/Header';
import QKDSimulator from './components/QKDSimulator';
import SessionHistory from './components/SessionHistory';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

// Context
import { AuthProvider } from './context/AuthContext';

type ThemeMode = 'light' | 'dark';

// Global Styles
const GlobalStyle = createGlobalStyle<{ themeMode: ThemeMode }>`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: ${({ themeMode }) =>
      themeMode === 'dark'
        ? 'linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%)'
        : 'linear-gradient(135deg, #f4f8ff 0%, #e5efff 100%)'};
    color: ${({ themeMode }) => (themeMode === 'dark' ? '#ffffff' : '#0b1c3a')};
    min-height: 100vh;
    overflow-x: hidden;
    transition: background 0.25s ease, color 0.25s ease;
  }

  html {
    scroll-behavior: smooth;
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
  }

  input, select {
    outline: none;
  }

  a {
    text-decoration: none;
    color: inherit;
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

function App() {
  const [themeMode, setThemeMode] = useState<ThemeMode>('dark');

  useEffect(() => {
    const savedTheme = localStorage.getItem('qkd_theme') as ThemeMode | null;
    if (savedTheme === 'light' || savedTheme === 'dark') {
      setThemeMode(savedTheme);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('qkd_theme', themeMode);
  }, [themeMode]);

  const toggleTheme = () => {
    setThemeMode((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <AuthProvider>
      <GlobalStyle themeMode={themeMode} />
      <Router>
        <AppContainer>
          <Header themeMode={themeMode} onToggleTheme={toggleTheme} />
          <MainContent>
            <Routes>
              <Route path="/" element={<Navigate to="/simulator" replace />} />
              <Route path="/simulator" element={<QKDSimulator />} />
              <Route path="/sessions" element={<SessionHistory />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </MainContent>
        </AppContainer>
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme={themeMode}
        />
      </Router>
    </AuthProvider>
  );
}

export default App;
