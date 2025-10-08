#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from sqlmodel import SQLModel, select
from backend.app.models import User, Agent, Strategy, Transaction, Performance, AgentStatus, StrategyType
from datetime import datetime

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/defai_agents"
)

async def test_basic_connection():
    print("\n" + "="*70)
    print("🔍 TEST 1: Basic Database Connection")
    print("="*70)
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to: {version.split(',')[0]}")
            
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Database name: {db_name}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_create_tables():
    print("\n" + "="*70)
    print("🔍 TEST 2: Creating Database Tables")
    print("="*70)
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            print("🗑️  Dropped existing tables")
            
            await conn.run_sync(SQLModel.metadata.create_all)
            print("📊 Created tables:")
            
            def get_tables(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_tables)
            for table in tables:
                print(f"   ✅ {table}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

async def test_insert_data():
    print("\n" + "="*70)
    print("🔍 TEST 3: Inserting Test Data")
    print("="*70)
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        
        engine = create_async_engine(DATABASE_URL, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            user = User(
                wallet_address="0x1234567890abcdef1234567890abcdef12345678",
                created_at=datetime.utcnow()
            )
            session.add(user)
            await session.flush()
            print(f"✅ Created user: {user.wallet_address} (ID: {user.id})")
            
            agent = Agent(
                user_id=user.id,
                name="Test Trading Agent",
                description="Automated yield farming agent",
                status=AgentStatus.PAUSED,
                risk_tolerance=0.7,
                max_position_size=5000.0,
                wallet_address="SoLaNA1234567890abcdefghijklmnopqrstuvwxyz",
                created_at=datetime.utcnow()
            )
            session.add(agent)
            await session.flush()
            print(f"✅ Created agent: {agent.name} (ID: {agent.id})")
            
            strategy = Strategy(
                agent_id=agent.id,
                strategy_type=StrategyType.YIELD_FARMING,
                name="SOL-USDC Yield Strategy",
                config='{"protocol": "raydium", "pool": "SOL-USDC"}',
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(strategy)
            await session.flush()
            print(f"✅ Created strategy: {strategy.name} (ID: {strategy.id})")
            
            transaction = Transaction(
                agent_id=agent.id,
                strategy_id=strategy.id,
                tx_hash="abc123def456",
                blockchain="solana",
                transaction_type="swap",
                amount=100.0,
                token_in="SOL",
                token_out="USDC",
                profit_loss=5.5,
                gas_fee=0.00005,
                status="completed",
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            session.add(transaction)
            await session.flush()
            print(f"✅ Created transaction: {transaction.tx_hash} (ID: {transaction.id})")
            
            performance = Performance(
                agent_id=agent.id,
                date=datetime.utcnow(),
                total_value=5500.0,
                daily_pnl=50.0,
                total_pnl=500.0,
                win_rate=0.75,
                total_trades=10,
                successful_trades=8
            )
            session.add(performance)
            await session.flush()
            print(f"✅ Created performance record (ID: {performance.id})")
            
            await session.commit()
            print("\n💾 All data committed successfully")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Data insertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_query_data():
    print("\n" + "="*70)
    print("🔍 TEST 4: Querying Data")
    print("="*70)
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        
        engine = create_async_engine(DATABASE_URL, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"\n📊 Users ({len(users)}):")
            for user in users:
                print(f"   - ID: {user.id}, Wallet: {user.wallet_address[:20]}...")
            
            result = await session.execute(select(Agent))
            agents = result.scalars().all()
            print(f"\n📊 Agents ({len(agents)}):")
            for agent in agents:
                print(f"   - ID: {agent.id}, Name: {agent.name}, Status: {agent.status}")
            
            result = await session.execute(select(Strategy))
            strategies = result.scalars().all()
            print(f"\n📊 Strategies ({len(strategies)}):")
            for strategy in strategies:
                print(f"   - ID: {strategy.id}, Type: {strategy.strategy_type}, Name: {strategy.name}")
            
            result = await session.execute(select(Transaction))
            transactions = result.scalars().all()
            print(f"\n📊 Transactions ({len(transactions)}):")
            for tx in transactions:
                print(f"   - ID: {tx.id}, Hash: {tx.tx_hash}, P/L: {tx.profit_loss}, Status: {tx.status}")
            
            result = await session.execute(select(Performance))
            performances = result.scalars().all()
            print(f"\n📊 Performance Records ({len(performances)}):")
            for perf in performances:
                print(f"   - Agent ID: {perf.agent_id}, Total P/L: ${perf.total_pnl}, Win Rate: {perf.win_rate*100:.1f}%")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_relationships():
    print("\n" + "="*70)
    print("🔍 TEST 5: Testing Foreign Key Relationships")
    print("="*70)
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        
        engine = create_async_engine(DATABASE_URL, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("""
                    SELECT u.wallet_address, COUNT(a.id) as agent_count
                    FROM users u
                    LEFT JOIN agents a ON u.id = a.user_id
                    GROUP BY u.id, u.wallet_address
                """)
            )
            print("\n📊 Users and their agents:")
            for row in result:
                print(f"   - Wallet: {row[0][:20]}... has {row[1]} agent(s)")
            
            result = await session.execute(
                text("""
                    SELECT a.name, COUNT(t.id) as tx_count, 
                           COALESCE(SUM(t.profit_loss), 0) as total_pnl
                    FROM agents a
                    LEFT JOIN transactions t ON a.id = t.agent_id
                    GROUP BY a.id, a.name
                """)
            )
            print("\n📊 Agents and their transactions:")
            for row in result:
                print(f"   - Agent: {row[0]}, Transactions: {row[1]}, Total P/L: ${row[2]:.2f}")
        
        await engine.dispose()
        print("\n✅ Relationship queries successful")
        return True
        
    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
        return False

async def main():
    print("\n" + "🚀"*35)
    print("    DeFAI Database Integration Test Suite")
    print("🚀"*35)
    print(f"\n📍 Testing database: {DATABASE_URL.split('@')[1]}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Create Tables", test_create_tables),
        ("Insert Data", test_insert_data),
        ("Query Data", test_query_data),
        ("Relationships", test_relationships)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Database is fully operational!")
        print("\n💡 Next steps:")
        print("   1. Start backend service: docker-compose up -d backend")
        print("   2. Check health: curl http://localhost:8000/health/db")
        print("   3. View logs: docker-compose logs -f backend")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

