import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../context/AuthContext';

type ThemeMode = 'light' | 'dark';

interface HeaderProps {
  themeMode: ThemeMode;
  onToggleTheme: () => void;
}

const HeaderContainer = styled.header<{ themeMode: ThemeMode }>`
  background: ${({ themeMode }) =>
    themeMode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.8)'};
  backdrop-filter: blur(10px);
  border-bottom: 1px solid
    ${({ themeMode }) =>
      themeMode === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(11, 28, 58, 0.12)'};
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Nav = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    transform: scale(1.05);
    transition: transform 0.2s ease;
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
  align-items: center;

  @media (max-width: 768px) {
    gap: 1rem;
  }
`;

const NavLink = styled(Link)<{ themeMode: ThemeMode }>`
  color: ${({ themeMode }) => (themeMode === 'dark' ? '#ffffff' : '#1a2a4a')};
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(0, 212, 255, 0.1);
    color: #00d4ff;
  }

  &.active {
    background: rgba(0, 212, 255, 0.2);
    color: #00d4ff;
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserInfo = styled.div<{ themeMode: ThemeMode }>`
  color: ${({ themeMode }) => (themeMode === 'dark' ? '#cccccc' : '#4b5f85')};
  font-size: 0.9rem;
`;

const LogoutButton = styled.button`
  background: linear-gradient(45deg, #ff4444, #cc0000);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(45deg, #cc0000, #aa0000);
    transform: translateY(-1px);
  }
`;

const LoginButton = styled(Link)`
  background: linear-gradient(45deg, #00d4ff, #0099cc);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(45deg, #0099cc, #007399);
    transform: translateY(-1px);
  }
`;

const ThemeToggleButton = styled.button<{ themeMode: ThemeMode }>`
  background: ${({ themeMode }) =>
    themeMode === 'dark'
      ? 'linear-gradient(45deg, #3d4f7c, #263b69)'
      : 'linear-gradient(45deg, #ffe08a, #ffbf47)'};
  color: ${({ themeMode }) => (themeMode === 'dark' ? '#ffffff' : '#2f2500')};
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    filter: brightness(0.95);
  }
`;

const Header: React.FC<HeaderProps> = ({ themeMode, onToggleTheme }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <HeaderContainer themeMode={themeMode}>
      <Nav>
        <Logo to="/simulator">
          QKD Simulator
        </Logo>

        <NavLinks>
          <NavLink themeMode={themeMode} to="/simulator">Simulator</NavLink>
          <NavLink themeMode={themeMode} to="/sessions">Sessions</NavLink>
          <NavLink themeMode={themeMode} to="/dashboard">Dashboard</NavLink>
          <ThemeToggleButton
            themeMode={themeMode}
            onClick={onToggleTheme}
            aria-label="Toggle dark and light theme"
          >
            {themeMode === 'dark' ? 'Light' : 'Dark'}
          </ThemeToggleButton>

          {user ? (
            <UserSection>
              <UserInfo themeMode={themeMode}>Welcome, {user.username}</UserInfo>
              <LogoutButton onClick={handleLogout}>
                Logout
              </LogoutButton>
            </UserSection>
          ) : (
            <LoginButton to="/login">
              Login
            </LoginButton>
          )}
        </NavLinks>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;
