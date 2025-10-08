# 🗄️ DeFAI Database Setup Guide

## Quick Start

### 1. Start PostgreSQL
```bash
docker compose up -d postgres
```

### 2. Verify It's Running
```bash
docker ps --filter "name=defai_postgres"
```

### 3. Run Tests
```bash
pip3 install asyncpg sqlalchemy sqlmodel greenlet
python3 quick_db_test.py
python3 test_db_integration.py
```

## Database Schema

### Tables Created
1. **users** - User accounts with wallet addresses
2. **agents** - AI trading agents
3. **strategies** - Trading strategies per agent
4. **transactions** - Transaction history
5. **performance** - Performance metrics

### Relationships
```
users (1) -----> (*) agents
agents (1) -----> (*) strategies
agents (1) -----> (*) transactions
agents (1) -----> (*) performance
```

## Common Commands

### Start/Stop Database
```bash
docker compose up -d postgres
docker compose stop postgres
docker compose down -v  # Remove volumes
```

### View Logs
```bash
docker logs defai_postgres
docker logs -f defai_postgres  # Follow logs
```

### Connect to Database
```bash
docker exec defai_postgres psql -U postgres -d defai_agents
```

### SQL Commands Inside Container
```sql
-- List tables
\dt

-- Describe table
\d users

-- Count records
SELECT COUNT(*) FROM users;

-- View all users with agents
SELECT u.wallet_address, COUNT(a.id) as agents 
FROM users u 
LEFT JOIN agents a ON u.id = a.user_id 
GROUP BY u.id;
```

### Python Connection
```python
import asyncpg

conn = await asyncpg.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    database='defai_agents'
)
```

## Health Checks

### Database Health
```bash
docker exec defai_postgres pg_isready -U postgres -d defai_agents
```

### Via Backend API (when running)
```bash
curl http://localhost:8000/health/db
```

## Troubleshooting

### Container Keeps Restarting
```bash
docker logs defai_postgres
docker system df  # Check disk space
docker system prune  # Clean up
```

### Port Already in Use
```bash
lsof -i :5432  # Find what's using port 5432
docker compose down  # Stop all services
```

### Connection Refused
- Wait 10 seconds after starting for initialization
- Check if container is running: `docker ps`
- Check logs: `docker logs defai_postgres`

### Reset Database
```bash
docker compose down -v
docker compose up -d postgres
sleep 10
python3 test_db_integration.py
```

## Configuration

### Connection String
```
postgresql+asyncpg://postgres:password@localhost:5432/defai_agents
```

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/defai_agents
POSTGRES_DB=defai_agents
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

## Next Steps

1. ✅ Database setup complete
2. 📝 Add Alembic migrations (TASK-002)
3. 🔄 Implement repository pattern (TASK-005)
4. 🚀 Deploy backend service with database

## Test Files

- `quick_db_test.py` - Quick connection test
- `test_database.py` - Basic asyncpg test
- `test_db_integration.py` - Full test suite
- `scripts/test-db.sh` - Automated testing

## Production Notes

⚠️ **Current Setup**: Using tmpfs (in-memory) storage for testing

**For Production**:
1. Change tmpfs to volume in docker-compose.yml:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

2. Add backup strategy
3. Use stronger passwords
4. Enable SSL connections
5. Configure proper user permissions

---

**Status**: ✅ Tested and Working  
**Last Updated**: October 7, 2025

