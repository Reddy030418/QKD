import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styled, { ThemeProvider as StyledThemeProvider, createGlobalStyle } from 'styled-components';
import type { DefaultTheme } from 'styled-components';

// Components
import Header from './components/Header';
import QKDSimulator from './components/QKDSimulator';
import SessionHistory from './components/SessionHistory';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

// Context
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { ThemeProvider, useThemeMode } from './context/ThemeContext';

const lightTheme: DefaultTheme = {
  name: 'light',
  colors: {
    background: '#f6f8fc',
    backgroundGradientStart: '#f6f8fc',
    backgroundGradientEnd: '#dbe8ff',
    text: '#0f1b2d',
    mutedText: '#4c5d78',
    cardBackground: 'rgba(255, 255, 255, 0.88)',
    cardBorder: 'rgba(15, 27, 45, 0.12)',
    accent: '#0a7cff',
    accentHover: '#005fcc',
    danger: '#d94343',
  },
};

const darkTheme: DefaultTheme = {
  name: 'dark',
  colors: {
    background: '#0f0f0f',
    backgroundGradientStart: '#0f0f0f',
    backgroundGradientEnd: '#1a1a2e',
    text: '#ffffff',
    mutedText: '#cccccc',
    cardBackground: 'rgba(255, 255, 255, 0.05)',
    cardBorder: 'rgba(255, 255, 255, 0.1)',
    accent: '#00d4ff',
    accentHover: '#0099cc',
    danger: '#ff4444',
  },
};

// Global Styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(
      135deg,
      ${({ theme }) => theme.colors.backgroundGradientStart} 0%,
      ${({ theme }) => theme.colors.backgroundGradientEnd} 100%
    );
    color: ${({ theme }) => theme.colors.text};
    min-height: 100vh;
    overflow-x: hidden;
    transition: background 0.2s ease, color 0.2s ease;
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
  return (
    <ThemeProvider>
      <AppShell />
    </ThemeProvider>
  );
}

const AppShell: React.FC = () => {
  const { mode } = useThemeMode();
  const activeTheme: DefaultTheme = mode === 'light' ? lightTheme : darkTheme;

  return (
    <StyledThemeProvider theme={activeTheme}>
      <AuthProvider>
        <ChatProvider>
          <GlobalStyle />
          <Router>
            <AppContainer>
              <Header />
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
              theme={mode}
            />
          </Router>
        </ChatProvider>
      </AuthProvider>
    </StyledThemeProvider>
  );
};

export default App;
