# 🔬 Quantum Key Distribution (QKD) Simulator

A comprehensive web application for simulating the BB84 Quantum Key Distribution protocol with real-time visualization, session management, and security analysis.

## ✨ Features

- **BB84 Protocol Simulation**: Complete implementation of the BB84 quantum key distribution protocol
- **Real-time Visualization**: Live updates during protocol execution via WebSocket
- **Interactive Controls**: Adjustable parameters for key length, noise level, and detector efficiency
- **Eavesdropping Simulation**: Optional Eve (eavesdropper) simulation with quantum noise
- **Security Analysis**: Real-time error rate calculation and security status assessment
- **Session Management**: Complete history of QKD sessions with detailed statistics
- **User Authentication**: Secure user registration and login system
- **Dashboard Analytics**: Comprehensive statistics and performance metrics
- **Responsive Design**: Modern, dark-themed UI that works on all devices

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based user authentication
- **WebSockets**: Real-time communication for live updates
- **QKD Protocol**: Complete BB84 implementation with quantum noise simulation

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Styled-components with CSS-in-JS
- **Charts**: Recharts for data visualization
- **Routing**: React Router for navigation
- **State Management**: React Context for authentication

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quantum-key-distribution
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   # Database will be created automatically on first run
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup
1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://qkd_user:qkd_password@localhost:5432/qkd_db

# Security Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# QKD Configuration
DEFAULT_KEY_LENGTH=50
DEFAULT_NOISE_LEVEL=5.0
DEFAULT_DETECTOR_EFFICIENCY=95.0
MAX_KEY_LENGTH=500
MIN_KEY_LENGTH=10

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### QKD Protocol
- `POST /qkd/run` - Run BB84 protocol simulation
- `GET /qkd/session/{session_id}` - Get session details
- `GET /qkd/stats` - Get QKD statistics
- `WS /qkd/ws` - WebSocket for real-time updates

### Sessions
- `GET /sessions/` - Get all sessions
- `GET /sessions/{session_id}` - Get specific session
- `DELETE /sessions/{session_id}` - Delete session
- `GET /sessions/stats/summary` - Get session statistics

## 🔬 BB84 Protocol Implementation

The application implements the complete BB84 protocol:

1. **Quantum State Preparation**: Alice generates random bits and bases
2. **Photon Transmission**: Quantum states are transmitted through a quantum channel
3. **Measurement**: Bob measures photons with randomly chosen bases
4. **Basis Reconciliation**: Alice and Bob compare bases to establish raw key
5. **Error Correction**: Statistical error detection and correction
6. **Privacy Amplification**: Final key extraction
7. **Security Analysis**: Error rate analysis to detect eavesdropping

### Parameters
- **Key Length**: Number of bits to generate (10-500)
- **Noise Level**: Quantum channel noise percentage (0-30%)
- **Detector Efficiency**: Photon detection efficiency (70-100%)
- **Eavesdropper**: Optional Eve simulation with additional noise

## 🔐 Security Features

- **Quantum Security**: BB84 protocol provides information-theoretic security
- **Error Rate Monitoring**: Automatic detection of eavesdropping attempts
- **Session Authentication**: JWT-based user authentication
- **Input Validation**: Comprehensive parameter validation
- **SQL Injection Protection**: Parameterized queries with SQLAlchemy

## 📈 Monitoring & Analytics

- **Real-time Progress**: Live updates during protocol execution
- **Session History**: Complete record of all QKD sessions
- **Performance Metrics**: Key generation rates and error statistics
- **Security Dashboard**: Visual analytics and trend analysis
- **Error Rate Analysis**: Statistical analysis of quantum channel quality

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Deployment
1. **Set environment variables**
   ```bash
   export NODE_ENV=production
   export DEBUG=False
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- BB84 protocol implementation based on research by Charles Bennett and Gilles Brassard
- Quantum noise simulation using realistic physical parameters
- UI design inspired by modern quantum computing interfaces

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting guide in the wiki

---

**⚠️ Disclaimer**: This is a simulation tool for educational purposes. It does not provide actual quantum security for real-world applications.
