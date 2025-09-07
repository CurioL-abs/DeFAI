# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

DeFAI is a DeFi yield optimization platform that combines AI-powered yield prediction with multi-chain smart contracts. The system consists of four main components:

1. **AI Service**: Machine learning models for yield prediction using gradient boosting
2. **Backend API**: FastAPI service that orchestrates AI predictions and manages strategies  
3. **Frontend**: Next.js application for user interaction
4. **Smart Contracts**: Both Ethereum (Solidity) and Solana (Anchor) vault implementations
5. **Agent Engine**: NEW - Autonomous AI agents for complex multi-step DeFi strategies

## Architecture

### Multi-Service Architecture
- **AI Service** (`ai/`): FastAPI on port 8001, handles ML inference
- **Backend** (`backend/`): FastAPI on port 8000, main API with auth
- **Agent Engine** (`agent-engine/`): FastAPI on port 8002, autonomous AI agents
- **Frontend** (`frontend/`): Next.js on port 3000, user interface
- **Smart Contracts** (`contracts/`): Dual-chain approach (Ethereum + Solana)
- **Database**: PostgreSQL with async SQLModel
- **Cache**: Redis for ML decision caching

### Enhanced Data Flow
1. Frontend requests agent creation via Backend API or Agent Engine
2. Agent Engine creates autonomous agents with ML-driven strategies
3. Agents continuously monitor market data and execute complex strategies
4. AI Service provides enhanced predictions with real-time market context
5. All actions are recorded in PostgreSQL for performance tracking

### Hybrid AI Agent Architecture
- **Off-chain Intelligence**: Complex ML processing in Agent Engine service
- **On-chain Execution**: Secure transaction execution via Solana contracts
- **Account Abstraction**: Agent wallets with automated signing
- **Multi-Protocol Support**: Jupiter, Marginfi, Orca, Raydium integration

## Common Development Commands

### Full Stack Development (Updated)
```bash
# Start all services with Docker Compose (now includes agent-engine + database)
docker-compose up --build

# Start individual services
docker-compose up postgres    # Database
docker-compose up redis       # Cache
docker-compose up backend     # Backend API
docker-compose up ai          # AI service only  
docker-compose up agent-engine # Agent engine
docker-compose up frontend    # Frontend only
```

### Agent Engine Development (NEW)
```bash
cd agent-engine
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Database migrations (when needed)
python -m alembic upgrade head

# Run with database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/defai_agents uvicorn main:app --reload --port 8002
```

### Frontend Development (Updated)
```bash
cd frontend
npm install
# Now includes agent engine endpoints
NEXT_PUBLIC_API=http://localhost:8000 NEXT_PUBLIC_AGENT_ENGINE=http://localhost:8002 npm run dev
```

### Testing Agent Strategies
```bash
# Create test agent via API
curl -X POST http://localhost:8002/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Agent","strategy_type":"yield_farming","risk_level":"medium"}'

# Start agent
curl -X POST http://localhost:8002/agents/{agent_id}/start

# Monitor performance
curl http://localhost:8002/agents/{agent_id}/performance
```

## Key Technical Details (Updated)

### Agent Engine Service
- **Autonomous Execution**: Background loops monitor and execute strategies
- **ML Integration**: Connects to existing AI service for enhanced decisions
- **Multi-Protocol**: Jupiter (swaps), Marginfi (lending), Orca (liquidity), Raydium (farming)
- **Performance Tracking**: Comprehensive metrics and portfolio snapshots
- **Risk Management**: Position limits, stop-loss, and risk assessment

### Database Schema
- **Agent**: Core agent configuration and performance metrics  
- **StrategyExecution**: Detailed execution logs with transaction IDs
- **AgentPerformance**: Daily/periodic performance snapshots
- **PortfolioSnapshot**: Point-in-time portfolio compositions
- **Strategy**: Reusable strategy templates

### API Endpoints (NEW)
- **Agent Management**: `/agents` - CRUD operations for AI agents
- **Strategy Templates**: `/strategies` - Reusable strategy configurations
- **Monitoring**: `/monitoring` - Dashboard, leaderboards, alerts
- **Analytics**: Real-time performance metrics and system health

### Enhanced ML Pipeline
- **Real-time Decisions**: ML interface processes live market data
- **Multi-step Strategies**: Sequential actions with conditional logic
- **Risk Assessment**: Dynamic risk scoring and position sizing
- **Market Adaptation**: Strategies adjust based on volatility and opportunities

### Account Abstraction (Solana)
- **Agent Wallets**: Program-derived addresses for each agent
- **Automated Signing**: Secure transaction execution without exposing keys
- **Gas Management**: Automatic fee handling and optimization
- **Multi-signature Support**: Enhanced security for high-value agents

## Environment Configuration (Updated)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/defai_agents

# Services
AI_SERVICE_URL=http://ai:8001
BACKEND_SERVICE_URL=http://backend:8000

# Blockchain
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
ALCHEMY_API_KEY=your_alchemy_key_here

# Cache
REDIS_URL=redis://redis:6379

# Auth (existing)
ADMIN_API_KEY=admin_demo_key_please_change
NEXT_PUBLIC_API=http://localhost:8000
NEXT_PUBLIC_AGENT_ENGINE=http://localhost:8002
```

## Development Notes (Updated)

### Agent Strategy Types
- **SWAP**: Token swapping via Jupiter aggregator
- **LENDING**: Deposit/borrow on Marginfi/Solend
- **LIQUIDITY_PROVISION**: AMM pool participation on Orca
- **YIELD_FARMING**: Staking for rewards on Raydium/Kamino
- **ARBITRAGE**: Cross-protocol price difference exploitation  
- **MULTI_HOP**: Complex multi-step strategies

### Business Model Integration
- **Performance Fees**: 10-20% on realized profits
- **Management Fees**: Optional 0.5% annual fee
- **Gas Pass-through**: Transparent blockchain costs
- **Agent Tokenization**: Future governance token integration

### Production Deployment
- **Database Scaling**: PostgreSQL with read replicas
- **Load Balancing**: Multiple agent-engine instances
- **Monitoring**: Comprehensive alerting and health checks
- **Security**: Multi-signature wallets and audit trails

## File Structure Highlights (Updated)

### Agent Engine Service (`agent-engine/`)
- `main.py`: FastAPI application with lifespan management
- `core/agent_manager.py`: Autonomous agent lifecycle management
- `core/strategy_engine.py`: Multi-protocol strategy execution
- `core/solana_client.py`: Blockchain integration with account abstraction
- `utils/ml_interface.py`: Enhanced ML decision interface
- `models/`: SQLModel database schemas (Agent, Strategy, Performance)
- `api/`: REST endpoints (agents, strategies, monitoring)

### Integration Points
- `docker-compose.yml`: Multi-service orchestration with database
- `ai/inference.py`: Enhanced to support agent decision making
- `backend/app/routes.py`: Integration with agent engine APIs
- `frontend/`: New agent management interface (to be implemented)

## Quick Start for New Developers

1. **Setup Database**: `docker-compose up postgres redis`
2. **Start Core Services**: `docker-compose up ai backend`
3. **Launch Agent Engine**: `docker-compose up agent-engine`
4. **Create Test Agent**: Use `/agents` API endpoint
5. **Monitor Performance**: Access `/monitoring/dashboard`

The hybrid architecture enables sophisticated AI-driven strategies while maintaining the security and transparency of blockchain execution.
