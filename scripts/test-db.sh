#!/bin/bash

set -e

echo "🔍 DeFAI Database Test Script"
echo "=============================="
echo ""

cd "$(dirname "$0")/.."

echo "1️⃣  Checking if PostgreSQL is running..."
if docker ps | grep -q defai_postgres; then
    echo "   ✅ PostgreSQL container is running"
else
    echo "   ⚠️  PostgreSQL not running. Starting it now..."
    docker-compose up -d postgres
    echo "   ⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
fi

echo ""
echo "2️⃣  Checking PostgreSQL health..."
docker-compose exec -T postgres pg_isready -U postgres -d defai_agents || {
    echo "   ⚠️  Database not ready yet. Waiting 10 more seconds..."
    sleep 10
    docker-compose exec -T postgres pg_isready -U postgres -d defai_agents
}
echo "   ✅ PostgreSQL is healthy"

echo ""
echo "3️⃣  Installing Python dependencies..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q asyncpg sqlalchemy sqlmodel 2>/dev/null || true
echo "   ✅ Dependencies ready"

echo ""
echo "4️⃣  Running basic connection test..."
python3 test_database.py

echo ""
echo "5️⃣  Running full integration test..."
python3 test_db_integration.py

echo ""
echo "=============================="
echo "✅ All tests completed!"
echo "=============================="

