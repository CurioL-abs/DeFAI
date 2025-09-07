# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

DeFAI is a DeFi yield optimization platform that combines AI-powered yield prediction with multi-chain smart contracts. The system consists of three main components:

1. **AI Service**: Machine learning models for yield prediction using gradient boosting
2. **Backend API**: FastAPI service that orchestrates AI predictions and manages strategies  
3. **Frontend**: Next.js application for user interaction
4. **Smart Contracts**: Both Ethereum (Solidity) and Solana (Anchor) vault implementations

## Architecture

### Multi-Service Architecture
- **AI Service** (`ai/`): FastAPI on port 8001, handles ML inference
- **Backend** (`backend/`): FastAPI on port 8000, main API with auth
- **Frontend** (`frontend/`): Next.js on port 3000, user interface
- **Smart Contracts** (`contracts/`): Dual-chain approach (Ethereum + Solana)

### Data Flow
1. Frontend requests strategy creation via Backend API
2. Backend authenticates with API key, calls AI service for prediction
3. AI service loads trained GradientBoostingRegressor model, returns yield prediction
4. Backend returns strategy with predicted yield to frontend

### Smart Contract Architecture
- **Ethereum**: Basic ERC4626-like vault in Solidity 0.8.19 with deposit/withdraw functionality
- **Solana**: Anchor program with similar vault logic using checked arithmetic

## Common Development Commands

### Full Stack Development
```bash
# Start all services with Docker Compose
docker-compose up --build

# Start services individually
docker-compose up backend  # Backend only
docker-compose up ai       # AI service only  
docker-compose up frontend # Frontend only
```

### Frontend Development (Next.js)
```bash
cd frontend
npm install
npm run dev        # Development server with turbopack
npm run build      # Production build with turbopack
npm run start      # Production server
npm run lint       # ESLint
```

### Backend Development (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### AI Service Development
```bash
cd ai
pip install -r requirements.txt
python train.py    # Train and save model
uvicorn inference:app --reload --port 8001
```

### Smart Contract Development

#### Ethereum (Foundry)
```bash
cd contracts/ethereum
forge build        # Compile contracts
forge test          # Run tests (if any exist)
forge script <script> --rpc-url <network> # Deploy
```

#### Solana (Anchor)
```bash
cd contracts/solana
anchor build        # Compile program
anchor deploy       # Deploy to configured network
anchor test         # Run tests (if any exist)
```

## Key Technical Details

### Authentication
- Backend uses bearer token authentication
- Default admin API key: `admin_demo_key_please_change` (set via `ADMIN_API_KEY` env var)
- AI service has no authentication (internal service)

### AI/ML Pipeline
- Uses scikit-learn GradientBoostingRegressor (200 estimators, max_depth=4)
- Model trained on synthetic data with 10 features
- Automatic model training on first run if no saved model exists
- Model saved as `models/lightgbm_model.joblib` (despite name, uses sklearn)

### API Structure
- Backend exposes `/strategies` POST endpoint for creating strategies
- AI service exposes `/predict` POST endpoint for yield prediction
- Both services include `/health` endpoints for monitoring

### Environment Configuration
- `ADMIN_API_KEY`: Backend authentication token
- `NEXT_PUBLIC_API`: Frontend API base URL (default: http://localhost:8000)
- Alchemy API key needed for Ethereum deployment (in foundry.toml)

## Development Notes

### Database
- Currently uses placeholder database initialization
- Backend includes SQLModel imports but no actual database implementation
- Ready for PostgreSQL/SQLite integration with SQLModel

### Smart Contract Limitations
- Ethereum contract uses basic 1:1 share:asset ratio (no complex yield calculations)
- Solana contract includes basic error handling with custom ErrorCode
- Neither contract implements actual yield generation logic

### Frontend State
- Currently shows default Next.js starter page
- Ready for React 19 and Next.js 15.5.2 development
- Uses Geist font family from Vercel

### Model Training
- Training data is synthetically generated with known patterns
- Model predicts yields based on strategy name hash for reproducibility
- No real market data integration currently implemented

## File Structure Highlights

- `ai/models/forecast_model.py`: Model loading with fallback dummy model
- `backend/app/routes.py`: Main API endpoint connecting to AI service  
- `contracts/ethereum/src/YieldVaultERC4626.sol`: Basic Solidity vault
- `contracts/solana/programs/yield_vault/src/lib.rs`: Anchor program
- `docker-compose.yml`: Service orchestration configuration
