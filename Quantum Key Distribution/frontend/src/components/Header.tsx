import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../context/AuthContext';
import { useThemeMode } from '../context/ThemeContext';

const HeaderContainer = styled.header`
  background: ${({ theme }) => theme.colors.cardBackground};
  backdrop-filter: blur(10px);
  border-bottom: 1px solid ${({ theme }) => theme.colors.cardBorder};
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

const NavLink = styled(Link)`
  color: ${({ theme }) => theme.colors.text};
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    background: ${({ theme }) => `${theme.colors.accent}22`};
    color: ${({ theme }) => theme.colors.accent};
  }

  &.active {
    background: ${({ theme }) => `${theme.colors.accent}33`};
    color: ${({ theme }) => theme.colors.accent};
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserInfo = styled.div`
  color: ${({ theme }) => theme.colors.mutedText};
  font-size: 0.9rem;
`;

const LogoutButton = styled.button`
  background: linear-gradient(45deg, ${({ theme }) => theme.colors.danger}, #aa0000);
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
  background: linear-gradient(45deg, ${({ theme }) => theme.colors.accent}, ${({ theme }) => theme.colors.accentHover});
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

const ThemeButton = styled.button`
  background: ${({ theme }) => `${theme.colors.accent}22`};
  color: ${({ theme }) => theme.colors.accent};
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  font-weight: 600;
`;

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useThemeMode();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <HeaderContainer>
      <Nav>
        <Logo to="/simulator">
          Quantum Data Pipeline & Security Analytics Engine
        </Logo>

        <NavLinks>
          <NavLink to="/simulator">Simulator</NavLink>
          <NavLink to="/sessions">Sessions</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <ThemeButton onClick={toggleTheme}>
            {mode === 'dark' ? 'Light' : 'Dark'}
          </ThemeButton>

          {user ? (
            <UserSection>
              <UserInfo>Welcome, {user.username}</UserInfo>
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
